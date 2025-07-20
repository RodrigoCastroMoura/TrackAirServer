import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Activity, Car, MessageSquare, Command } from "lucide-react";
import { Vehicle } from "@shared/gps-schema";

export default function Dashboard() {
  const { data: vehicles = [], isLoading } = useQuery<Vehicle[]>({
    queryKey: ["/api/vehicles"],
  });

  const onlineVehicles = vehicles.filter(v => v.status === "online");
  const blockedVehicles = vehicles.filter(v => v.blocked);
  const pendingCommands = vehicles.filter(v => v.blockCommandPending);

  if (isLoading) {
    return (
      <div className="min-h-screen w-full flex items-center justify-center">
        <div className="text-lg">Loading dashboard...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">GPS Tracking Dashboard</h1>
        
        {/* Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Vehicles</CardTitle>
              <Car className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{vehicles.length}</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Online Vehicles</CardTitle>
              <Activity className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{onlineVehicles.length}</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Blocked Vehicles</CardTitle>
              <MessageSquare className="h-4 w-4 text-red-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">{blockedVehicles.length}</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Pending Commands</CardTitle>
              <Command className="h-4 w-4 text-orange-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-orange-600">{pendingCommands.length}</div>
            </CardContent>
          </Card>
        </div>

        {/* Recent Vehicles */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Vehicle Activity</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {vehicles.slice(0, 10).map((vehicle) => (
                <div key={vehicle.id} className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex items-center space-x-4">
                    <div className="flex-shrink-0">
                      <Car className="h-8 w-8 text-gray-600" />
                    </div>
                    <div>
                      <div className="font-medium">{vehicle.plate || vehicle.imei}</div>
                      <div className="text-sm text-gray-500">IMEI: {vehicle.imei}</div>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <Badge 
                      variant={vehicle.status === "online" ? "default" : "secondary"}
                      className={vehicle.status === "online" ? "bg-green-100 text-green-800" : ""}
                    >
                      {vehicle.status}
                    </Badge>
                    
                    {vehicle.blocked && (
                      <Badge variant="destructive">Blocked</Badge>
                    )}
                    
                    {vehicle.blockCommandPending && (
                      <Badge variant="outline" className="border-orange-500 text-orange-700">
                        Command Pending
                      </Badge>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
