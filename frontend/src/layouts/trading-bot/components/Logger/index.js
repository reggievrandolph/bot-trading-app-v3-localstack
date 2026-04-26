import React, { useEffect, useState } from "react";
import io from "socket.io-client";

// @mui material components
import Card from "@mui/material/Card";

import Grid from "@mui/material/Grid";
import DataTable from "examples/Tables/DataTable";

// Material Dashboard 2 React components
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";

import TimelineList from "examples/Timeline/TimelineList";
import TimelineItem from "examples/Timeline/TimelineItem";

import { convertTo12Hour } from "../../../../utils/timeUtils";

function Logger() {
  const [rows, setLogs] = useState([]);

  const columns = [
    { Header: "Timestamp", accessor: "timestamp", align: "left" },
    { Header: "Symbol", accessor: "symbol", align: "left" },
    { Header: "Event", accessor: "event", align: "left" },
    { Header: "Action", accessor: "action", align: "left" },
    { Header: "Trigger", accessor: "trigger", align: "left" },
    { Header: "Price", accessor: "price", align: "left" },
    { Header: "Contract", accessor: "contract", align: "left" },
    { Header: "PnL", accessor: "pnl", align: "left" },
    { Header: "Id", accessor: "id", align: "left" },
  ];

  useEffect(() => {
    const socket = io("http://localhost:5001");

    socket.on("ORDER_ACTIVITY_STREAM", function (data) {
      console.log("Received data from ORDER_ACTIVITY_STREAM:", data);
      setLogs((prevLogs) => [
        {
          event: data.event_type,
          symbol: data.symbol,
          timestamp: convertTo12Hour(data.timestamp.toString()),
          action: data.action,
          price: data.price,
          contract: data.contract,
          id: data.position_id || data.order_id,
          pnl: isNaN(parseFloat(data.pnl)) ? "" : parseFloat(data.pnl) * 100,
          trigger: data.trigger,
        },
        ...prevLogs,
      ]);
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
    <MDBox pt={6} pb={3}>
      <Grid container spacing={6}>
        <Grid item xs={12}>
          <Card>
            <MDBox
              mx={2}
              mt={-3}
              py={3}
              px={2}
              variant="gradient"
              bgColor="info"
              borderRadius="lg"
              coloredShadow="info"
            >
              <MDTypography variant="h6" color="white">
                Activity Log
              </MDTypography>
            </MDBox>
            <MDBox pt={3}>
              <DataTable
                table={{ columns, rows }}
                isSorted={false}
                entriesPerPage={true}
                showTotalEntries={true}
                canSearch={true}
                noEndBorder
              />
            </MDBox>
          </Card>
        </Grid>
      </Grid>
    </MDBox>
  );
}

export default Logger;
