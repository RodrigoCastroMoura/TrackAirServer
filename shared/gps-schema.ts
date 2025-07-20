import { pgTable, text, serial, integer, boolean, timestamp, jsonb } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";

export const vehicles = pgTable("vehicles", {
  id: serial("id").primaryKey(),
  imei: text("imei").notNull().unique(),
  cpf: text("cpf"),
  plate: text("plate"),
  ignition: boolean("ignition"),
  blocked: boolean("blocked").default(false),
  blockCommandPending: boolean("block_command_pending").default(false),
  blockWarningSent: boolean("block_warning_sent").default(false),
  trackerModel: text("tracker_model"),
  trackerPassword: text("tracker_password"),
  status: text("status").default("offline"), // online, offline, blocked
  lastSeen: timestamp("last_seen"),
  createdAt: timestamp("created_at").defaultNow(),
});

export const vehicleData = pgTable("vehicle_data", {
  id: serial("id").primaryKey(),
  imei: text("imei").notNull(),
  longitude: text("longitude"),
  latitude: text("latitude"),
  altitude: text("altitude"),
  speed: text("speed"),
  ignition: boolean("ignition"),
  timestamp: timestamp("timestamp").defaultNow(),
  deviceTime: text("device_time"),
  rawData: text("raw_data"),
});

export const commands = pgTable("commands", {
  id: serial("id").primaryKey(),
  imei: text("imei").notNull(),
  commandType: text("command_type").notNull(), // GTOUT, GTSRI, GTBSI
  commandData: text("command_data").notNull(),
  parameters: jsonb("parameters").$type<Record<string, any>>(),
  status: text("status").default("pending"), // pending, sent, acknowledged, failed
  createdAt: timestamp("created_at").defaultNow(),
  sentAt: timestamp("sent_at"),
  acknowledgedAt: timestamp("acknowledged_at"),
  retryCount: integer("retry_count").default(0),
  maxRetries: integer("max_retries").default(3),
  timeoutSeconds: integer("timeout_seconds").default(30),
});

export const deviceConfigurations = pgTable("device_configurations", {
  id: serial("id").primaryKey(),
  imei: text("imei").notNull().unique(),
  serverIp: text("server_ip"),
  serverPort: integer("server_port"),
  serverDomain: text("server_domain"),
  apnName: text("apn_name"),
  apnUsername: text("apn_username"),
  apnPassword: text("apn_password"),
  reportInterval: integer("report_interval"),
  heartbeatInterval: integer("heartbeat_interval"),
  updatedAt: timestamp("updated_at").defaultNow(),
  appliedAt: timestamp("applied_at"),
});

export const messages = pgTable("messages", {
  id: serial("id").primaryKey(),
  cpf: text("cpf"),
  imei: text("imei"),
  messageTypeId: integer("message_type_id").notNull(),
  message: text("message").notNull(),
  messageHtml: text("message_html"),
  timestamp: timestamp("timestamp").defaultNow(),
  read: boolean("read").default(false),
});

// Insert schemas
export const insertVehicleSchema = createInsertSchema(vehicles).omit({
  id: true,
  createdAt: true,
});

export const insertVehicleDataSchema = createInsertSchema(vehicleData).omit({
  id: true,
  timestamp: true,
});

export const insertCommandSchema = createInsertSchema(commands).omit({
  id: true,
  createdAt: true,
  sentAt: true,
  acknowledgedAt: true,
});

export const insertDeviceConfigurationSchema = createInsertSchema(deviceConfigurations).omit({
  id: true,
  updatedAt: true,
  appliedAt: true,
});

export const insertMessageSchema = createInsertSchema(messages).omit({
  id: true,
  timestamp: true,
});

// Types
export type Vehicle = typeof vehicles.$inferSelect;
export type InsertVehicle = z.infer<typeof insertVehicleSchema>;

export type VehicleData = typeof vehicleData.$inferSelect;
export type InsertVehicleData = z.infer<typeof insertVehicleDataSchema>;

export type Command = typeof commands.$inferSelect;
export type InsertCommand = z.infer<typeof insertCommandSchema>;

export type DeviceConfiguration = typeof deviceConfigurations.$inferSelect;
export type InsertDeviceConfiguration = z.infer<typeof insertDeviceConfigurationSchema>;

export type Message = typeof messages.$inferSelect;
export type InsertMessage = z.infer<typeof insertMessageSchema>;
