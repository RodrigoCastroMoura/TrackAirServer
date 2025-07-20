import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Command as CommandIcon, Shield, Server, Wifi, Clock } from "lucide-react";
import { Vehicle, Command } from "@shared/gps-schema";
import { apiRequest, queryClient } from "@/lib/queryClient";
import { useToast } from "@/hooks/use-toast";
import CommandForm from "@/components/command-form";

export default function Commands() {
  const { toast } = useToast();
  const [selectedImei, setSelectedImei] = useState("");
  
  const { data: vehicles = [] } = useQuery<Vehicle[]>({
    queryKey: ["/api/vehicles"],
  });

  const { data: commands = [] } = useQuery<Command[]>({
    queryKey: ["/api/vehicles", selectedImei, "commands"],
    enabled: !!selectedImei,
  });

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <h1 className="text-2xl font-bold text-gray-900">Command Center</h1>
          <p className="text-gray-600 mt-1">Send commands and manage device configurations</p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto p-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Command Forms */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <CommandIcon className="h-5 w-5" />
                  Send Commands
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="device-select">Select Device</Label>
                    <Select value={selectedImei} onValueChange={setSelectedImei}>
                      <SelectTrigger>
                        <SelectValue placeholder="Choose a device..." />
                      </SelectTrigger>
                      <SelectContent>
                        {vehicles.map((vehicle) => (
                          <SelectItem key={vehicle.id} value={vehicle.imei}>
                            {vehicle.plate || vehicle.imei} - {vehicle.imei}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  {selectedImei && (
                    <Tabs defaultValue="block">
                      <TabsList className="grid w-full grid-cols-3">
                        <TabsTrigger value="block" className="flex items-center gap-2">
                          <Shield className="h-4 w-4" />
                          Block
                        </TabsTrigger>
                        <TabsTrigger value="server" className="flex items-center gap-2">
                          <Server className="h-4 w-4" />
                          Server
                        </TabsTrigger>
                        <TabsTrigger value="apn" className="flex items-center gap-2">
                          <Wifi className="h-4 w-4" />
                          APN
                        </TabsTrigger>
                      </TabsList>

                      <TabsContent value="block">
                        <CommandForm 
                          type="block" 
                          imei={selectedImei} 
                          vehicle={vehicles.find(v => v.imei === selectedImei)} 
                        />
                      </TabsContent>

                      <TabsContent value="server">
                        <CommandForm 
                          type="server" 
                          imei={selectedImei} 
                          vehicle={vehicles.find(v => v.imei === selectedImei)} 
                        />
                      </TabsContent>

                      <TabsContent value="apn">
                        <CommandForm 
                          type="apn" 
                          imei={selectedImei} 
                          vehicle={vehicles.find(v => v.imei === selectedImei)} 
                        />
                      </TabsContent>
                    </Tabs>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Command History */}
          <div>
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Clock className="h-5 w-5" />
                  Command History
                  {selectedImei && (
                    <Badge variant="outline" className="ml-2">
                      {vehicles.find(v => v.imei === selectedImei)?.plate || selectedImei}
                    </Badge>
                  )}
                </CardTitle>
              </CardHeader>
              <CardContent>
                {!selectedImei ? (
                  <div className="text-center text-gray-500 py-8">
                    Select a device to view command history
                  </div>
                ) : commands.length === 0 ? (
                  <div className="text-center text-gray-500 py-8">
                    No commands found for this device
                  </div>
                ) : (
                  <div className="space-y-4">
                    {commands.map((command) => (
                      <div
                        key={command.id}
                        className="border rounded-lg p-4 space-y-2"
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <Badge variant="outline">
                              {command.commandType}
                            </Badge>
                            <span className="text-sm font-medium">
                              {command.parameters?.action || command.commandType}
                            </span>
                          </div>
                          <Badge
                            variant={
                              command.status === "acknowledged"
                                ? "default"
                                : command.status === "sent"
                                ? "secondary"
                                : command.status === "failed"
                                ? "destructive"
                                : "outline"
                            }
                          >
                            {command.status}
                          </Badge>
                        </div>
                        
                        <div className="text-sm text-gray-600">
                          <div>Created: {new Date(command.createdAt).toLocaleString()}</div>
                          {command.sentAt && (
                            <div>Sent: {new Date(command.sentAt).toLocaleString()}</div>
                          )}
                          {command.acknowledgedAt && (
                            <div>Acknowledged: {new Date(command.acknowledgedAt).toLocaleString()}</div>
                          )}
                        </div>
                        
                        {command.parameters && Object.keys(command.parameters).length > 0 && (
                          <div className="text-xs bg-gray-50 p-2 rounded">
                            <div className="font-medium mb-1">Parameters:</div>
                            <pre className="whitespace-pre-wrap">
                              {JSON.stringify(command.parameters, null, 2)}
                            </pre>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
