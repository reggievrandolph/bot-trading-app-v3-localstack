// @mui material components
import Grid from "@mui/material/Grid";

// Material Dashboard 2 React components
import MDBox from "components/MDBox";

// Material Dashboard 2 React examples
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";

// Billing page components
import Logger from "layouts/trading-bot/components/Logger";
import Ticker from "layouts/trading-bot/components/Ticker";
import Bot from "layouts/trading-bot/components/Bot";
import Account from "layouts/trading-bot/components/Account";
import PriceLogger from "layouts/trading-bot/components/PriceLogger";
import Strategy from "./components/Strategy";

function Billing() {
  return (
    <DashboardLayout>
      <DashboardNavbar absolute isMini />
      <MDBox mt={8}>
        <MDBox mb={3}>
          <Grid container spacing={3}>
            {/* Stack Bot and Strategy */}
            <Grid item xs={12} lg={3}>
              <Grid container direction="column" spacing={2}>
                <Grid item>
                  <Bot />
                </Grid>
                <Grid item>
                  <Strategy />
                </Grid>
              </Grid>
            </Grid>

            {/* Other items */}
            <Grid item xs={12} lg={3}>
              <Ticker />
            </Grid>
            <Grid item xs={12} lg={3}>
              <Account />
            </Grid>
          </Grid>
        </MDBox>

        <MDBox mb={3}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Logger />
            </Grid>
          </Grid>
        </MDBox>
      </MDBox>
      <Footer />
    </DashboardLayout>
  );
}

export default Billing;
