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

function PriceLogger() {
  const [rows, setLogs] = useState([]);

  const columns = [
    { Header: "Messages", accessor: "message", width: "45%", align: "left" },
    { Header: "Timestamp", accessor: "timestamp", align: "left" },
  ];

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
                Price Log
              </MDTypography>
            </MDBox>
            <MDBox pt={3}>
              <TimelineList>
                {rows.map((row, index) => (
                  <TimelineItem
                    key={index}
                    title={row.message}
                    description={row.data}
                    dateTime={row.timestamp}
                    icon="notifications"
                    iconColor="info"
                  />
                ))}
              </TimelineList>
              {/* <DataTable
                table={{ columns, rows }}
                isSorted={false}
                entriesPerPage={true}
                showTotalEntries={true}
                canSearch={true}
                noEndBorder
              /> */}
            </MDBox>
          </Card>
        </Grid>
      </Grid>
    </MDBox>
  );
}

export default PriceLogger;
