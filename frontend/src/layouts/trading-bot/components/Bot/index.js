import { useState, useRef, useEffect } from "react";
import { Card } from "@mui/material";
import MDButton from "components/MDButton";
import CircularProgress from "@mui/material/CircularProgress";
import { useMaterialUIController } from "context";
import { Stack, CardContent, Box } from "@mui/material";
import { Alert } from "@mui/material";

function Bot() {
  const [controller] = useMaterialUIController();

  const [mode, setMode] = useState("OFFLINE"); // null until loaded

  useEffect(() => {
    fetch("http://localhost:5001/mode")
      .then((res) => res.json())
      .then((data) => {
        setMode(data.mode);
        console.log("MODE:", data.mode);
      })
      .catch((error) => console.log("ERROR", error));
  }, []);

  return (
    <Card sx={{ minWidth: 275, minHeight: 90, textAlign: "center", padding: 1 }}>
      <div style={{ fontWeight: "bold" }}>Status</div>
      {mode && (
        <div
          style={{
            padding: "4px 8px",
            borderRadius: "4px",
            fontSize: "0.85rem",
            fontWeight: "bold",
            color: "#000",
            backgroundColor:
              mode === "simulated"
                ? "#fef3c7" // yellow/beige
                : mode === "live"
                ? "#dbeafe" // blue
                : "#e5e7eb", // gray for offline
            display: "inline-block",
            marginBottom: "8px",
          }}
        >
          {mode === "simulated" ? "SIMULATION MODE" : mode === "live" ? "LIVE MODE" : "OFFLINE"}
        </div>
      )}
    </Card>
  );
}

export default Bot;
