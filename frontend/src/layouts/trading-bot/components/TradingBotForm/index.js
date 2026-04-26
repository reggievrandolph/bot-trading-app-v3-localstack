import React, { useState } from "react";
import {
  TextField,
  Button,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  Box,
  Grid,
  NativeSelect,
  Stack,
} from "@mui/material";
import MDButton from "components/MDButton";

const TradingBotForm = () => {
  const [stockPrice, setStockPrice] = useState("");
  const [strategy, setStrategy] = useState("");

  const handleStart = () => {
    console.log("Starting bot with stock price:", stockPrice, "and strategy:", strategy);
    // Add logic to start the bot
  };

  const handleStop = () => {
    console.log("Stopping bot");
    // Add logic to stop the bot
  };

  return (
    <Grid container spacing={1}>
      <TextField id="outlined-basic" label="Outlined" variant="outlined" />
      <Stack spacing={2}>
        <MDButton color="success">Start</MDButton>
        <MDButton color="error">Stop</MDButton>
      </Stack>
    </Grid>
  );
};

export default TradingBotForm;
