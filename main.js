const { Collection, Intents, Client } = require('discord.js');
const fs = require('fs');
const path = require('path');
const { token } = require('./config.json');
const commands = require('./events/registerCommands');
const client = new Client({ intents: [Intents.FLAGS.GUILDS, Intents.FLAGS.GUILD_MESSAGES] });
client.commands = new Collection();
const commandsPath = path.join(__dirname, 'commands');
const commandFiles = fs.readdirSync(commandsPath).filter(file => file.endsWith('.js'));

for (const file of commandFiles) {
  const filePath = path.join(commandsPath, file);
  const command = require(filePath);
  client.commands.set(command.data.name, command);
}
const lockFile = 'main.lck';
fs.writeFileSync(lockFile, '');
client.once('ready', () => {
  console.clear();
  console.log('\n\n');
  fs.readFile('./assets/header.txt', 'utf8', (err, data) => {
    if (err) {
      console.error('Error reading art file:', err);
      return;
    }
    console.log(data);
    console.log('\n\n');
    console.log(`Logged in: ${client.user.tag}`);
    console.log('\n');
    console.log('Flare is a modified version of AKoD, coded specificly to support Ubuntu and Linux. Check out my orginal project at https://github.com.tagoworks/akod');
    console.log('In order for Flare to be working you need to have the Flask API, Discord bot, this watcher, and Cloudflare docker all running at the same time.');
    console.log('\n');
    console.log('--------------------LOGGING-------------------');
    client.user.setPresence({ status: 'online', activities: [{ name: 'licenses', type: 'WATCHING' }] });
  });
});

client.on('interactionCreate', async interaction => {
  if (!interaction.isCommand()) return;
  const command = client.commands.get(interaction.commandName);
  if (!command) return;

  try {
    await command.execute(interaction);
  } catch (error) {
    console.error(error);
    await interaction.reply({ content: 'There was an error while executing this command!', ephemeral: true });
  }
});

process.on('exit', () => {
  fs.unlinkSync(lockFile);
});
process.on('SIGINT', () => {
  fs.unlinkSync(lockFile);
  process.exit();
});
client.login(token);