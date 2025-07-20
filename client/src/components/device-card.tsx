import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Car, MapPin, Activity, Shield, Settings } from "lucide-react";
import { Vehicle } from "@shared/gps-schema";
import { Link } from "wouter";

interface DeviceCardProps {
  vehicle: Vehicle;
}

export default function DeviceCard({ vehicle }: DeviceCardProps) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case "online":
        return "bg-green-100 text-green-800 border-green-200";
      case "offline":
        return "bg-gray-100 text-gray-800 border-gray-200";
      case "blocked":
        return "bg-red-100 text-red-800 border-red-200";
      default:
        return "bg-gray-100 text-gray-800 border-gray-200";
    }
  };

  return (
    <Card className="hover:shadow-lg transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg flex items-center gap-2">
            <Car className="h-5 w-5 text-blue-600" />
            {vehicle.plate || `Device ${vehicle.imei.slice(-4)}`}
          </CardTitle>
          <Badge className={getStatusColor(vehicle.status)}>
            {vehicle.status}
          </Badge>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Device Info */}
        <div className="space-y-2 text-sm">
          <div className="flex items-center justify-between">
            <span className="text-gray-600">IMEI:</span>
            <span className="font-mono">{vehicle.imei}</span>
          </div>
          
          {vehicle.cpf && (
            <div className="flex items-center justify-between">
              <span className="text-gray-600">CPF:</span>
              <span>{vehicle.cpf}</span>
            </div>
          )}
          
          {vehicle.trackerModel && (
            <div className="flex items-center justify-between">
              <span className="text-gray-600">Model:</span>
              <span>{vehicle.trackerModel}</span>
            </div>
          )}
          
          {vehicle.lastSeen && (
            <div className="flex items-center justify-between">
              <span className="text-gray-600">Last Seen:</span>
              <span>{new Date(vehicle.lastSeen).toLocaleString()}</span>
            </div>
          )}
        </div>

        {/* Status Indicators */}
        <div className="flex flex-wrap gap-2">
          {vehicle.ignition !== null && (
            <Badge 
              variant="outline" 
              className={vehicle.ignition ? "border-green-500 text-green-700" : "border-gray-500"}
            >
              <Activity className="h-3 w-3 mr-1" />
              {vehicle.ignition ? "Ignition On" : "Ignition Off"}
            </Badge>
          )}
          
          {vehicle.blocked && (
            <Badge variant="destructive">
              <Shield className="h-3 w-3 mr-1" />
              Blocked
            </Badge>
          )}
          
          {vehicle.blockCommandPending && (
            <Badge variant="outline" className="border-orange-500 text-orange-700">
              Command Pending
            </Badge>
          )}
        </div>

        {/* Actions */}
        <div className="flex gap-2 pt-2">
          <Link href={`/vehicles/${vehicle.imei}`}>
            <Button variant="outline" size="sm" className="flex-1">
              <MapPin className="h-4 w-4 mr-1" />
              View
            </Button>
          </Link>
          
          <Link href={`/commands`}>
            <Button variant="outline" size="sm" className="flex-1">
              <Settings className="h-4 w-4 mr-1" />
              Commands
            </Button>
          </Link>
        </div>
      </CardContent>
    </Card>
  );
}
