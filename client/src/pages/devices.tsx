import { useQuery } from "@tanstack/react-query";
import { Link } from "wouter";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Search, Settings, MapPin, Activity } from "lucide-react";
import { Vehicle } from "@shared/gps-schema";
import { useState } from "react";
import DeviceCard from "@/components/device-card";

export default function Devices() {
  const [searchTerm, setSearchTerm] = useState("");
  
  const { data: vehicles = [], isLoading } = useQuery<Vehicle[]>({
    queryKey: ["/api/vehicles"],
  });

  const filteredVehicles = vehicles.filter(vehicle => 
    vehicle.imei.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (vehicle.plate && vehicle.plate.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  if (isLoading) {
    return (
      <div className="min-h-screen w-full flex items-center justify-center">
        <div className="text-lg">Loading devices...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-gray-900">GPS Devices</h1>
            <Link href="/commands">
              <Button>
                <Settings className="h-4 w-4 mr-2" />
                Manage Commands
              </Button>
            </Link>
          </div>
          
          {/* Search */}
          <div className="mt-4 max-w-md">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                type="text"
                placeholder="Search by IMEI or plate..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Device Grid */}
      <div className="max-w-7xl mx-auto p-6">
        {filteredVehicles.length === 0 ? (
          <Card className="text-center py-12">
            <CardContent>
              <div className="text-gray-500">
                {vehicles.length === 0 ? "No devices found" : "No devices match your search"}
              </div>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredVehicles.map((vehicle) => (
              <DeviceCard key={vehicle.id} vehicle={vehicle} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
