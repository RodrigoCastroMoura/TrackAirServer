import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Vehicle } from "@shared/gps-schema";
import { apiRequest, queryClient } from "@/lib/queryClient";
import { useToast } from "@/hooks/use-toast";
import { Shield, Server, Wifi } from "lucide-react";

interface CommandFormProps {
  type: "block" | "server" | "apn";
  imei: string;
  vehicle?: Vehicle;
}

export default function CommandForm({ type, imei, vehicle }: CommandFormProps) {
  const { toast } = useToast();
  const [formData, setFormData] = useState<any>({});

  const mutation = useMutation({
    mutationFn: async (data: any) => {
      let endpoint = "";
      switch (type) {
        case "block":
          endpoint = `/api/vehicles/${imei}/commands/block`;
          break;
        case "server":
          endpoint = `/api/vehicles/${imei}/commands/server-config`;
          break;
        case "apn":
          endpoint = `/api/vehicles/${imei}/commands/apn-config`;
          break;
      }
      
      return apiRequest("POST", endpoint, data);
    },
    onSuccess: () => {
      toast({
        title: "Command sent successfully",
        description: `${type} command has been queued for device ${imei}`,
      });
      
      queryClient.invalidateQueries({ queryKey: ["/api/vehicles", imei, "commands"] });
      setFormData({});
    },
    onError: (error: any) => {
      toast({
        title: "Failed to send command",
        description: error.message || "An error occurred while sending the command",
        variant: "destructive",
      });
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    mutation.mutate(formData);
  };

  const updateFormData = (key: string, value: any) => {
    setFormData((prev: any) => ({ ...prev, [key]: value }));
  };

  const renderBlockForm = () => (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="flex items-center space-x-2">
        <Switch
          id="block-switch"
          checked={formData.block || false}
          onCheckedChange={(value) => updateFormData("block", value)}
        />
        <Label htmlFor="block-switch">
          {formData.block ? "Block Device" : "Unblock Device"}
        </Label>
      </div>

      <div>
        <Label htmlFor="tracker-model">Tracker Model</Label>
        <Select 
          value={formData.trackerModel || vehicle?.trackerModel || "GV50"} 
          onValueChange={(value) => updateFormData("trackerModel", value)}
        >
          <SelectTrigger>
            <SelectValue placeholder="Select tracker model" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="GV50">GV50</SelectItem>
            <SelectItem value="GV300">GV300</SelectItem>
            <SelectItem value="GMT200">GMT200</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div>
        <Label htmlFor="password">Device Password</Label>
        <Input
          id="password"
          type="password"
          placeholder="Enter device password"
          value={formData.password || vehicle?.trackerPassword || ""}
          onChange={(e) => updateFormData("password", e.target.value)}
        />
      </div>

      <Button type="submit" disabled={mutation.isPending} className="w-full">
        <Shield className="h-4 w-4 mr-2" />
        {mutation.isPending ? "Sending..." : `${formData.block ? "Block" : "Unblock"} Device`}
      </Button>
    </form>
  );

  const renderServerForm = () => (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <Label htmlFor="server-ip">Server IP Address</Label>
        <Input
          id="server-ip"
          type="text"
          placeholder="192.168.1.100"
          value={formData.serverIp || ""}
          onChange={(e) => updateFormData("serverIp", e.target.value)}
          required
        />
      </div>

      <div>
        <Label htmlFor="server-port">Server Port</Label>
        <Input
          id="server-port"
          type="number"
          placeholder="8000"
          value={formData.serverPort || ""}
          onChange={(e) => updateFormData("serverPort", parseInt(e.target.value))}
          required
        />
      </div>

      <div>
        <Label htmlFor="password">Device Password</Label>
        <Input
          id="password"
          type="password"
          placeholder="Enter device password"
          value={formData.password || vehicle?.trackerPassword || ""}
          onChange={(e) => updateFormData("password", e.target.value)}
        />
      </div>

      <Button type="submit" disabled={mutation.isPending} className="w-full">
        <Server className="h-4 w-4 mr-2" />
        {mutation.isPending ? "Sending..." : "Configure Server"}
      </Button>
    </form>
  );

  const renderApnForm = () => (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <Label htmlFor="apn-name">APN Name</Label>
        <Input
          id="apn-name"
          type="text"
          placeholder="internet.provider.com"
          value={formData.apnName || ""}
          onChange={(e) => updateFormData("apnName", e.target.value)}
          required
        />
      </div>

      <div>
        <Label htmlFor="apn-username">APN Username</Label>
        <Input
          id="apn-username"
          type="text"
          placeholder="Optional username"
          value={formData.apnUsername || ""}
          onChange={(e) => updateFormData("apnUsername", e.target.value)}
        />
      </div>

      <div>
        <Label htmlFor="apn-password">APN Password</Label>
        <Input
          id="apn-password"
          type="password"
          placeholder="Optional password"
          value={formData.apnPassword || ""}
          onChange={(e) => updateFormData("apnPassword", e.target.value)}
        />
      </div>

      <div>
        <Label htmlFor="device-password">Device Password</Label>
        <Input
          id="device-password"
          type="password"
          placeholder="Enter device password"
          value={formData.password || vehicle?.trackerPassword || ""}
          onChange={(e) => updateFormData("password", e.target.value)}
        />
      </div>

      <Button type="submit" disabled={mutation.isPending} className="w-full">
        <Wifi className="h-4 w-4 mr-2" />
        {mutation.isPending ? "Sending..." : "Configure APN"}
      </Button>
    </form>
  );

  switch (type) {
    case "block":
      return renderBlockForm();
    case "server":
      return renderServerForm();
    case "apn":
      return renderApnForm();
    default:
      return null;
  }
}
