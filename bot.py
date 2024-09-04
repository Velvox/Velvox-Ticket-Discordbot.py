import discord
from discord.ext import commands
from discord import app_commands
import pymysql
import config
import io

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents, help_command=None)

def get_db_connection():
    return pymysql.connect(
        host=config.DB_HOST,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        database=config.DB_NAME
    )

get_db_connection_tickets = get_db_connection

@bot.event
async def on_ready():
    print(f'[INFO] Logged in as {bot.user}')
    await bot.tree.sync()  # Sync slash commands
    activity = discord.Activity(type=discord.ActivityType.watching, name="New tickets")
    await bot.change_presence(activity=activity)
    print(f'[INFO] Activity set')

@bot.tree.command(name="ticketlaunch", description="Create a ticket button")
@commands.has_permissions(administrator=True)
async def ticketlaunch(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Create a Ticket",
        description="Click a button below to open a ticket for the corresponding request type.\n\n **⚙️ General Questions** for all general questions.\n **🤝 Partnership Request** If you want to request a partnership with this server.\n**📝 Apply for Staff** If you want to apply for staff.",
        color=discord.Color.purple()  # Using predefined purple color
    )
    view = discord.ui.View()

    buttons = [
        discord.ui.Button(label="⚙️ General Questions", style=discord.ButtonStyle.primary, custom_id="ticket_general"),
        discord.ui.Button(label="🤝 Partnership Request", style=discord.ButtonStyle.success, custom_id="ticket_partnership"),
        discord.ui.Button(label="📝 Apply for Staff", style=discord.ButtonStyle.secondary, custom_id="ticket_apply_staff")
    ]

    for button in buttons:
        view.add_item(button)

    await interaction.response.send_message(embed=embed, view=view)

@bot.tree.command(name="setrole", description="Set a role to manage tickets")
@commands.has_permissions(administrator=True)
async def setticketrole(interaction: discord.Interaction, role: discord.Role):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO roles (role_id) VALUES (%s)", (str(role.id),))
    connection.commit()
    cursor.close()
    connection.close()
    embed = discord.Embed(
        title="Role Set",
        description=f"Role {role.name} has been set to manage tickets.",
        color=discord.Color.green()  # Using predefined green color
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="removerole", description="Remove a role from managing tickets")
@commands.has_permissions(administrator=True)
async def removeticketrole(interaction: discord.Interaction, role: discord.Role):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM roles WHERE role_id = %s", (str(role.id),))
    connection.commit()
    cursor.close()
    connection.close()
    embed = discord.Embed(
        title="Role Removed",
        description=f"Role {role.name} has been removed from managing tickets.",
        color=discord.Color.red()  # Using predefined red color
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="adduser", description="Add a user to the ticket")
async def adduser(interaction: discord.Interaction, member: discord.Member):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM tickets WHERE channel_id = %s", (str(interaction.channel.id),))
    ticket = cursor.fetchone()
    cursor.close()
    connection.close()

    if not ticket:
        embed = discord.Embed(
            title="Error",
            description="No ticket found.",
            color=discord.Color.red()  # Using predefined red color
        )
        await interaction.response.send_message(embed=embed)
        return

    await interaction.channel.set_permissions(member, read_messages=True, send_messages=True)
    embed = discord.Embed(
        title="User Added",
        description=f"Added {member.mention} to the ticket.",
        color=discord.Color.green()  # Using predefined green color
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="removeuser", description="Remove a user from the ticket")
async def removeuser(interaction: discord.Interaction, member: discord.Member):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM tickets WHERE channel_id = %s", (str(interaction.channel.id),))
    ticket = cursor.fetchone()
    cursor.close()
    connection.close()

    if not ticket:
        embed = discord.Embed(
            title="Error",
            description="No ticket found.",
            color=discord.Color.red()  # Using predefined red color
        )
        await interaction.response.send_message(embed=embed)
        return

    await interaction.channel.set_permissions(member, read_messages=False, send_messages=False)
    embed = discord.Embed(
        title="User Removed",
        description=f"Removed {member.mention} from the ticket.",
        color=discord.Color.green()  # Using predefined green color
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ticketsetcategory", description="Set a category for tickets")
@commands.has_permissions(administrator=True)
async def setticketcategory(interaction: discord.Interaction, category: discord.CategoryChannel):
    guild_id = interaction.guild.id  # Get the guild ID from the interaction
    
    connection = get_db_connection()  # Assuming get_db_connection() returns a database connection
    cursor = connection.cursor()
    
    # Clear the existing category setting for the specific guild
    cursor.execute("DELETE FROM ticket_category WHERE guild_id = %s", (str(guild_id),))
    
    # Insert the new category ID for the specific guild
    cursor.execute("INSERT INTO ticket_category (guild_id, category_id) VALUES (%s, %s)", (str(guild_id), str(category.id)))
    
    connection.commit()
    cursor.close()
    connection.close()
    
    embed = discord.Embed(
        title="Category Set",
        description=f"Tickets will now be created under the category: {category.name}.",
        color=discord.Color.green()  # Using predefined green color
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="setupticketdatabase", description="Set up the database tables for the ticket system")
@commands.has_permissions(administrator=True)
async def setupticketdatabase(interaction: discord.Interaction):
    # Connect to the database
    connection = get_db_connection()
    cursor = connection.cursor()

    # SQL statements to create necessary tables
    create_roles_table = """
    CREATE TABLE IF NOT EXISTS roles (
        role_id VARCHAR(255) PRIMARY KEY
    );
    """

    create_ticket_category_table = """
    CREATE TABLE IF NOT EXISTS ticket_category (
        guild_id VARCHAR(255) PRIMARY KEY,
        category_id VARCHAR(255) NOT NULL
    );
    """

    create_tickets_table = """
    CREATE TABLE IF NOT EXISTS tickets (
        ticket_id INT AUTO_INCREMENT PRIMARY KEY,
        user_id VARCHAR(255) NOT NULL,
        channel_id VARCHAR(255) NOT NULL,
        status VARCHAR(50) NOT NULL,
        type VARCHAR(100) NOT NULL,
        guild_id VARCHAR(255) NOT NULL
    );
    """

    # Execute the SQL statements
    try:
        cursor.execute(create_roles_table)
        cursor.execute(create_ticket_category_table)
        cursor.execute(create_tickets_table)
        connection.commit()

        embed = discord.Embed(
            title="✅ Database Setup Complete",
            description="All necessary database tables have been created successfully.\n Or they where already there.",
            color=discord.Color.green()  # Using predefined green color
        )
    except Exception as e:
        embed = discord.Embed(
            title="❌ Database Setup Failed",
            description=f"An error occurred while setting up the database: {e}",
            color=discord.Color.red()  # Using predefined red color
        )
    finally:
        cursor.close()
        connection.close()

    await interaction.response.send_message(embed=embed, ephemeral=True)

def get_allowed_roles():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT role_id FROM roles")
    roles = cursor.fetchall()
    cursor.close()
    connection.close()
    return [int(role[0]) for role in roles]

@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.component:
        custom_id = interaction.data.get("custom_id")
        if custom_id == "ticket_general":
            await handle_open_ticket(interaction, "General Questions")
        elif custom_id == "ticket_partnership":
            await handle_open_ticket(interaction, "Partnership Request")
        elif custom_id == "ticket_apply_staff":
            await handle_open_ticket(interaction, "Apply for Staff")
        elif custom_id == "close_ticket":
            await handle_close_ticket(interaction)
        elif custom_id == "confirm_close":
            await confirm_close_ticket(interaction)
        elif custom_id == "cancel_close":
            await cancel_close_ticket(interaction)

async def handle_open_ticket(interaction: discord.Interaction, ticket_type: str):
    await interaction.response.defer()  # Acknowledge the interaction

    guild_id = interaction.guild.id
    connection = get_db_connection_tickets()  # Use the config function to get the connection
    
    try:
        with connection.cursor() as cursor:
            # Fetch the category ID associated with the guild
            cursor.execute("SELECT category_id FROM ticket_category WHERE guild_id = %s", (str(guild_id),))
            result = cursor.fetchone()

            category = None
            if result:
                category_id = int(result['category_id'])
                print(f"Retrieved category ID: {category_id} for guild ID: {guild_id}")
                category = interaction.guild.get_channel(category_id)
            else:
                print(f"No category found for guild ID: {guild_id}")

            # Create a new ticket channel under the specified category
            channel_name = f'ticket-{interaction.user.name}'
            if category:
                channel = await category.create_text_channel(channel_name)
            else:
                channel = await interaction.guild.create_text_channel(channel_name)

            # Insert the new ticket into the database
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO tickets (user_id, channel_id, status, type, guild_id) VALUES (%s, %s, %s, %s, %s)",
                               (str(interaction.user.id), str(channel.id), 'open', ticket_type, str(guild_id)))
                connection.commit()
                print(f"Inserted ticket for user ID {interaction.user.id} into database.")

            # Close the connection after the insert operation
            connection.close()

            # Directly set permissions for the ticket creator
            try:
                # Set permissions for the ticket creator to view and send messages in the ticket channel
                await channel.set_permissions(interaction.user, view_channel=True, send_messages=True)
                print(f"Successfully added {interaction.user.name} to the channel '{channel_name}'.")
            except Exception as e:
                print(f"Failed to add {interaction.user.name} to the channel '{channel_name}'. Error: {e}")
                await channel.send("There was an error adding you to the channel.")

            # Set up the embed and buttons
            embed = discord.Embed(
                title="Ticket Created",
                description=f'{interaction.user.mention}, your ticket for **{ticket_type}** has been created {channel.mention}.',
                color=discord.Color.purple()
            )

            view = discord.ui.View()
            close_button = discord.ui.Button(label="Close Ticket", style=discord.ButtonStyle.danger, custom_id="close_ticket")
            view.add_item(close_button)

            await channel.send(embed=embed, view=view)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Ensure the connection is closed in case of an exception
        if connection.open:
            connection.close()

    await interaction.followup.send(embed=embed, ephemeral=True)

async def handle_close_ticket(interaction: discord.Interaction):
    # Ensure that interaction is acknowledged
    await interaction.response.defer()  # This sends an acknowledgment response
    
    # Check if the ticket exists
    connection = get_db_connection_tickets()  # Update to use your specific connection function
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM tickets WHERE channel_id = %s", (str(interaction.channel.id),))
    ticket = cursor.fetchone()
    cursor.close()
    connection.close()

    if not ticket:
        embed = discord.Embed(
            title="Error",
            description="No ticket found.",
            color=discord.Color.red()  # Using predefined red color
        )
        await interaction.followup.send(embed=embed)  # Use followup.send for follow-up responses
        return

    # Check if the user has the required role
    allowed_roles = get_allowed_roles()
    if not any(role.id in allowed_roles for role in interaction.user.roles):
        embed = discord.Embed(
            title="Permission Denied",
            description="You do not have permission to close this ticket.",
            color=discord.Color.red()  # Using predefined red color
        )
        await interaction.followup.send(embed=embed)
        return

    # Confirm closure
    confirmation_embed = discord.Embed(
        title="Close Ticket",
        description="Are you sure you want to close this ticket?",
        color=discord.Color.red()  # Using predefined red color
    )
    view = discord.ui.View()
    yes_button = discord.ui.Button(label="Yes", style=discord.ButtonStyle.success, custom_id="confirm_close")
    no_button = discord.ui.Button(label="No", style=discord.ButtonStyle.danger, custom_id="cancel_close")
    view.add_item(yes_button)
    view.add_item(no_button)
    
    # Send the confirmation embed
    await interaction.followup.send(embed=confirmation_embed, view=view)

async def handle_close_ticket(interaction: discord.Interaction):
    # Ensure that interaction is acknowledged
    await interaction.response.defer()  # This sends an acknowledgment response
    
    # Check if the ticket exists
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM tickets WHERE channel_id = %s", (str(interaction.channel.id),))
    ticket = cursor.fetchone()
    cursor.close()
    connection.close()

    if not ticket:
        embed = discord.Embed(
            title="Error",
            description="No ticket found.",
            color=discord.Color.red()  # Using predefined red color
        )
        await interaction.followup.send(embed=embed)  # Use followup.send for follow-up responses
        return

    # Check if the user has the required role
    allowed_roles = get_allowed_roles()
    if not any(role.id in allowed_roles for role in interaction.user.roles):
        embed = discord.Embed(
            title="Permission Denied",
            description="You do not have permission to close this ticket.",
            color=discord.Color.red()  # Using predefined red color
        )
        await interaction.followup.send(embed=embed)
        return

    # Confirm closure
    confirmation_embed = discord.Embed(
        title="Close Ticket",
        description="Are you sure you want to close this ticket?",
        color=discord.Color.red()  # Using predefined red color
    )
    view = discord.ui.View()
    yes_button = discord.ui.Button(label="Yes", style=discord.ButtonStyle.success, custom_id="confirm_close")
    no_button = discord.ui.Button(label="No", style=discord.ButtonStyle.danger, custom_id="cancel_close")
    view.add_item(yes_button)
    view.add_item(no_button)
    
    # Send the confirmation embed
    await interaction.followup.send(embed=confirmation_embed, view=view)

async def confirm_close_ticket(interaction: discord.Interaction):
    # Check if the ticket exists in the database
    connection = get_db_connection_tickets()  # Update to use your specific connection function
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM tickets WHERE channel_id = %s", (str(interaction.channel.id),))
    ticket = cursor.fetchone()

    if not ticket:
        cursor.close()
        connection.close()
        embed = discord.Embed(
            title="Error",
            description="No ticket found.",
            color=discord.Color.red()  # Using predefined red color
        )
        await interaction.response.send_message(embed=embed)
        return

    # Accessing tuple data using indices
    user_id = int(ticket[1])  # Adjust index based on your table structure

    # Create and send the transcript
    transcript = io.StringIO()
    async for message in interaction.channel.history(limit=200):  # Adjust the limit as needed
        transcript.write(f"{message.author}: {message.content}\n")
    transcript.seek(0)  # Reset file pointer to the beginning

    # Attempt to fetch the user
    try:
        user = await interaction.client.fetch_user(user_id)
        try:
            # Send the transcript to the user via DM
            await user.send("Here is the transcript of your ticket:", file=discord.File(fp=transcript, filename="transcript.txt"))
            print(f"Sent ticket transcript to user ID {user_id}.")
        except discord.Forbidden:
            print(f"Failed to send DM to user ID {user_id}.")
        except Exception as e:
            print(f"An error occurred while sending the transcript: {e}")
    except discord.NotFound:
        print(f"User with ID {user_id} not found.")
    except Exception as e:
        print(f"An error occurred while fetching the user: {e}")

    # Delete the ticket entry from the database
    cursor.execute("DELETE FROM tickets WHERE channel_id = %s", (str(interaction.channel.id),))
    connection.commit()
    cursor.close()
    connection.close()

    # Delete the ticket channel
    await interaction.channel.delete()

async def cancel_close_ticket(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Cancelled",
        description="Ticket closing has been cancelled.",
        color=discord.Color.purple()  # Using predefined purple color
    )
    await interaction.response.send_message(embed=embed)

bot.run(config.DISCORD_TOKEN)
