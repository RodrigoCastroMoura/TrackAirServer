import { Router } from "express";
import { z } from "zod";
import { insertCommandSchema, insertDeviceConfigurationSchema } from "@shared/gps-schema";
import { storage } from "./storage";

const router = Router();

// Get all vehicles
router.get("/vehicles", async (req, res) => {
  try {
    const vehicles = await storage.getAllVehicles();
    res.json(vehicles);
  } catch (error) {
    res.status(500).json({ error: "Failed to fetch vehicles" });
  }
});

// Get vehicle by IMEI
router.get("/vehicles/:imei", async (req, res) => {
  try {
    const { imei } = req.params;
    const vehicle = await storage.getVehicleByImei(imei);
    
    if (!vehicle) {
      return res.status(404).json({ error: "Vehicle not found" });
    }
    
    res.json(vehicle);
  } catch (error) {
    res.status(500).json({ error: "Failed to fetch vehicle" });
  }
});

// Get vehicle tracking data
router.get("/vehicles/:imei/data", async (req, res) => {
  try {
    const { imei } = req.params;
    const { limit = "100" } = req.query;
    
    const data = await storage.getVehicleData(imei, parseInt(limit as string));
    res.json(data);
  } catch (error) {
    res.status(500).json({ error: "Failed to fetch vehicle data" });
  }
});

// Send block/unblock command
router.post("/vehicles/:imei/commands/block", async (req, res) => {
  try {
    const { imei } = req.params;
    const { block, trackerModel = "GV50", password = "" } = req.body;
    
    const commandData = {
      imei,
      commandType: "GTOUT",
      commandData: generateBlockCommand(block, trackerModel, password),
      parameters: { block, trackerModel, action: block ? "block" : "unblock" },
    };
    
    const command = await storage.createCommand(commandData);
    res.json({ success: true, commandId: command.id });
  } catch (error) {
    res.status(500).json({ error: "Failed to send block command" });
  }
});

// Send server configuration command
router.post("/vehicles/:imei/commands/server-config", async (req, res) => {
  try {
    const { imei } = req.params;
    const { serverIp, serverPort, password = "" } = req.body;
    
    const commandData = {
      imei,
      commandType: "GTSRI",
      commandData: generateServerConfigCommand(serverIp, serverPort, password),
      parameters: { serverIp, serverPort, action: "server_config" },
    };
    
    const command = await storage.createCommand(commandData);
    res.json({ success: true, commandId: command.id });
  } catch (error) {
    res.status(500).json({ error: "Failed to send server config command" });
  }
});

// Send APN configuration command
router.post("/vehicles/:imei/commands/apn-config", async (req, res) => {
  try {
    const { imei } = req.params;
    const { apnName, apnUsername = "", apnPassword = "", password = "" } = req.body;
    
    const commandData = {
      imei,
      commandType: "GTBSI",
      commandData: generateApnConfigCommand(apnName, apnUsername, apnPassword, password),
      parameters: { apnName, apnUsername, action: "apn_config" },
    };
    
    const command = await storage.createCommand(commandData);
    res.json({ success: true, commandId: command.id });
  } catch (error) {
    res.status(500).json({ error: "Failed to send APN config command" });
  }
});

// Get commands for a device
router.get("/vehicles/:imei/commands", async (req, res) => {
  try {
    const { imei } = req.params;
    const commands = await storage.getCommandsByImei(imei);
    res.json(commands);
  } catch (error) {
    res.status(500).json({ error: "Failed to fetch commands" });
  }
});

// Get device configuration
router.get("/vehicles/:imei/configuration", async (req, res) => {
  try {
    const { imei } = req.params;
    const config = await storage.getDeviceConfiguration(imei);
    res.json(config || {});
  } catch (error) {
    res.status(500).json({ error: "Failed to fetch device configuration" });
  }
});

// Update device configuration
router.put("/vehicles/:imei/configuration", async (req, res) => {
  try {
    const { imei } = req.params;
    const configData = insertDeviceConfigurationSchema.parse({ ...req.body, imei });
    
    const config = await storage.upsertDeviceConfiguration(configData);
    res.json(config);
  } catch (error) {
    if (error instanceof z.ZodError) {
      return res.status(400).json({ error: "Invalid configuration data", details: error.errors });
    }
    res.status(500).json({ error: "Failed to update device configuration" });
  }
});

// Get messages for a user
router.get("/messages/:cpf", async (req, res) => {
  try {
    const { cpf } = req.params;
    const { limit = "50" } = req.query;
    
    const messages = await storage.getMessagesByCpf(cpf, parseInt(limit as string));
    res.json(messages);
  } catch (error) {
    res.status(500).json({ error: "Failed to fetch messages" });
  }
});

// Helper functions for command generation
function generateBlockCommand(block: boolean, trackerModel: string, password: string): string {
  const bit = block ? "1" : "0";
  const counter = `000${bit}`;
  
  switch (trackerModel) {
    case "GMT200":
      return `AT+GTOUT=${password},${bit},0,0,0,,,,,,,,,,${counter}$`;
    case "GV300":
      return `AT+GTOUT=${password},${bit},,,0,0,0,0,5,1,0,,1,1,,,${counter}$`;
    case "GV50":
    default:
      return `AT+GTOUT=${password},${bit},,,,,,0,,,,,,,${counter}$`;
  }
}

function generateServerConfigCommand(serverIp: string, serverPort: number, password: string): string {
  return `AT+GTSRI=${password},${serverIp},${serverPort},,,0001$`;
}

function generateApnConfigCommand(apnName: string, apnUsername: string, apnPassword: string, password: string): string {
  return `AT+GTBSI=${password},${apnName},${apnUsername},${apnPassword},,,0001$`;
}

export default router;
