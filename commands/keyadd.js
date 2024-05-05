const { SlashCommandBuilder } = require('@discordjs/builders');
const fs = require('fs');
const path = require('path');
const { ownerID, guildID } = require('../config.json');
const logFilePath = path.join(__dirname, '..', 'flare.log');
function logToFile(message) {
  const now = new Date();
  const timestamp = `[BOT-${now.getHours()}:${now.getMinutes()}:${now.getSeconds()}]`;
  const logMessage = `${timestamp} ${message}\n`;

  fs.appendFile(logFilePath, logMessage, (err) => {
    if (err) {
      console.error('Error writing to log file:', err);
    }
  });
}
module.exports = {
  data: new SlashCommandBuilder()
    .setName('keyadd')
    .setDescription('Add a new key to the list of valid keys')
    .addStringOption(option =>
      option
        .setName('key')
        .setDescription('The activation key to add')
        .setRequired(true)
    )
    .addStringOption(option =>
      option
        .setName('lock')
        .setDescription('Type of license locker')
        .addChoices(
          { name: 'IP Address', value: 'IP' },
          { name: 'Machine HWID', value: 'HWID' }
        )
    ),
    async execute(interaction) {
      logToFile(`Received interaction: ${interaction}`);
    
      if (interaction.user.id !== ownerID) {
        logToFile(`Unauthorized access attempted by user: ${interaction.user.id}`);
        return interaction.reply({ content: 'You are not allowed to use this command.', ephemeral: true });
      }
    
      const licenseKeyToAdd = interaction.options.getString('key');
      const licenseLockType = interaction.options.getString('lock');
      logToFile(`Received license key to add: ${licenseKeyToAdd}`);
      logToFile(`Received license lock type: ${licenseLockType}`);
    
      const licenseFilePath = path.join(__dirname, '..', 'assets', 'validkeys.txt');
      logToFile(`Reading file from path: ${licenseFilePath}`);
    
      fs.readFile(licenseFilePath, 'utf8', (err, data) => {
        if (err) {
          logToFile(`Error reading key file: ${err}`);
          return interaction.reply({ content: 'Error adding key. Please try again later.', ephemeral: true });
        }
    
        if (existingKeys.includes(licenseKeyToAdd)) {
          logToFile(`Key already exists: ${licenseKeyToAdd}`);
          return interaction.reply({ content: 'This key already exists.', ephemeral: true });
        }
    
        fs.writeFile(licenseFilePath, newData, (err) => {
          if (err) {
            logToFile(`Error adding key: ${err}`);
            return interaction.reply({ content: 'Error adding key. Please try again later.', ephemeral: true });
          }
    
          logToFile(`Key added successfully: ${licenseKeyToAdd}`);
          const licenseLockerMessage = licenseLockType ? ` with ${licenseLockType} lock` : '';
          return interaction.reply({ content: `Activation key ${licenseKeyToAdd}${licenseLockerMessage} added successfully.`, ephemeral: true });
        });
      });
    },
  defaultPermission: false,
  permissions: [
    { id: guildID, type: 'ROLE', permission: false },
    { id: ownerID, type: 'USER', permission: true },
  ],
};
