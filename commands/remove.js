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
    .setName('remove')
    .setDescription('Remove a registered account')
    .addStringOption(option =>
      option
        .setName('account-name')
        .setDescription('The account name to remove')
        .setRequired(true)
    ),
  async execute(interaction) {
    logToFile(`Received interaction: ${interaction}`);

    if (!ownerID) {
      logToFile('Owner information not found in config.');
      return interaction.reply({ content: 'Owner information not found in config.', ephemeral: true });
    }

    if (interaction.user.id !== ownerID) {
      logToFile(`Unauthorized access attempted by user: ${interaction.user.id}`);
      return interaction.reply({ content: 'You do not have permission to use this command.', ephemeral: true });
    }

    const accToRemove = interaction.options.getString('account-name');
    logToFile(`Received account name to remove: ${accToRemove}`);

    const assetsFolderPath = path.join(__dirname, '..', 'assets', 'registered');
    logToFile(`Assets folder path: ${assetsFolderPath}`);

    const accFolder = path.join(assetsFolderPath, accToRemove);
    logToFile(`Account folder path to remove: ${accFolder}`);

    fs.rm(accFolder, { recursive: true }, (err) => {
      if (err) {
        logToFile(`Error removing account folder: ${err}`);
        return interaction.reply({ content: 'Error removing account folder. Please try again later.', ephemeral: true });
      }

      logToFile(`Account folder deleted successfully: ${accToRemove}`);
      return interaction.reply({ content: `Account ${accToRemove} deleted successfully.`, ephemeral: true });
    });
  },
  permissions: [
    { id: guildID, type: 'ROLE', permission: false },
    { id: ownerID, type: 'USER', permission: true },
  ],
};