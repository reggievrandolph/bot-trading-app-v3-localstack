import React, { useEffect, useState } from "react";
import io from "socket.io-client";
import { Card } from "@mui/material";

function Account() {
  const [value, setValue] = useState("0.00"); // Move useState outside of useEffect
  const [cashBalance, setCashBalance] = useState("0.00"); // Move useState outside of useEffect

  useEffect(() => {
    const socket = io("http://localhost:5001");

    // Listen for data from ACCOUNT_ACTIVITY_STREAM
    socket.on("ACCOUNT_ACTIVITY_STREAM", function (data) {
      console.log("Received data from ACCOUNT_ACTIVITY_STREAM:", data);
      setValue(data.cumulative_pnl);
    });

    // Handle connection
    socket.on("connect", function () {
      console.log("Connected to server");
    });

    // Handle disconnection
    socket.on("disconnect", () => {
      console.log("Disconnected from the server");
    });

    // Clean up on component unmount
    return () => {
      socket.disconnect();
    };
  }, []);

  useEffect(() => {
    const socket = io("http://localhost:5001");

    // Listen for data from ACCOUNT_DETAILS_STREAM
    socket.on("ACCOUNT_DETAILS_STREAM", function (data) {
      console.log("Received data from ACCOUNT_DETAILS_STREAM:", data);
      setCashBalance(data.cash_balance);
    });

    // Handle connection
    socket.on("connect", function () {
      console.log("Connected to server");
    });

    // Handle disconnection
    socket.on("disconnect", () => {
      console.log("Disconnected from the server");
    });

    // Clean up on component unmount
    return () => {
      socket.disconnect();
    };
  }, []);

  return (
    <Card sx={{ minWidth: 565, minHeight: 195, textAlign: "center", padding: 1 }}>
      <div style={{ fontWeight: "bold" }}>Account</div>
      <div>PnL: {value}</div>
      <div>Cash Balance: {cashBalance}</div>
    </Card>
  );
}

export default Account;
