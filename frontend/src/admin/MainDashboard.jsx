import React from "react";
import DashboardCard from "./DashboardCard";
import "./MainDashboard.css";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  LineChart,
  Line,
  ResponsiveContainer,
} from "recharts";

function MainDashboard() {
  // Dummy Data
  const dummyData = {
    stats: {
      todayRentals: 64,
      ongoingRentals: 32,
      dueReturns: 16,
      todayReturns: 8,
    },
    salesChartData: [
      { date: "2025-01-01", sales: 100 },
      { date: "2025-01-02", sales: 120 },
      { date: "2025-01-03", sales: 90 },
      { date: "2025-01-04", sales: 150 },
      { date: "2025-01-05", sales: 200 },
      { date: "2025-01-06", sales: 170 },
      { date: "2025-01-07", sales: 130 },
    ],
    maintenanceData: [
      { month: "Jan", cost: 500 },
      { month: "Feb", cost: 700 },
      { month: "Mar", cost: 400 },
      { month: "Apr", cost: 900 },
      { month: "May", cost: 600 },
      { month: "Jun", cost: 800 },
    ],
    moduleOptionPopularityData: [
      { name: "Module A", count: 120 },
      { name: "Module B", count: 90 },
      { name: "Module C", count: 150 },
      { name: "Option X", count: 200 },
      { name: "Option Y", count: 110 },
    ],
    vehiclesStatusData: [
      { name: "Active", value: 80 },
      { name: "Inactive", value: 10 },
      { name: "Maintenance", value: 10 },
    ],
    modulesStatusData: [
      { name: "Active", value: 50 },
      { name: "Inactive", value: 20 },
      { name: "Maintenance", value: 30 },
    ],
    optionsStatusData: [
      { name: "Active", value: 70 },
      { name: "Inactive", value: 15 },
      { name: "Maintenance", value: 15 },
    ],
  };

  // 색상 배열 (PieChart용)
  const COLORS = ["#0088FE", "#00C49F", "#FFBB28"];

  return (
    <div className="main-dashboard">
      <h1>대시보드</h1>

      {/* 1. Stats Cards */}
      <div className="dashboard-grid">
        <DashboardCard
          title="오늘 대여된 차량"
          value={dummyData.stats.todayRentals}
        />
        <DashboardCard
          title="대여 중인 차량"
          value={dummyData.stats.ongoingRentals}
        />
        <DashboardCard
          title="오늘 반납될 차량"
          value={dummyData.stats.dueReturns}
        />
        <DashboardCard
          title="오늘 반납된 차량"
          value={dummyData.stats.todayReturns}
        />
      </div>

      {/* 2. Fleet Utilization & 상태 분포 */}
      <div className="section">
        <h2>상태 차트</h2>
        <div className="fleet-utilization">
          <div className="pie-chart-container">
            <h4>차량</h4>
            <PieChart width={250} height={250}>
              <Pie
                data={dummyData.vehiclesStatusData}
                cx="50%"
                cy="50%"
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
                label
              >
                {dummyData.vehiclesStatusData.map((entry, index) => (
                  <Cell
                    key={`cell-veh-${index}`}
                    fill={COLORS[index % COLORS.length]}
                  />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </div>
          <div className="pie-chart-container">
            <h4>모듈</h4>
            <PieChart width={250} height={250}>
              <Pie
                data={dummyData.modulesStatusData}
                cx="50%"
                cy="50%"
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
                label
              >
                {dummyData.modulesStatusData.map((entry, index) => (
                  <Cell
                    key={`cell-mod-${index}`}
                    fill={COLORS[index % COLORS.length]}
                  />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </div>
          <div className="pie-chart-container">
            <h4>옵션</h4>
            <PieChart width={250} height={250}>
              <Pie
                data={dummyData.optionsStatusData}
                cx="50%"
                cy="50%"
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
                label
              >
                {dummyData.optionsStatusData.map((entry, index) => (
                  <Cell
                    key={`cell-opt-${index}`}
                    fill={COLORS[index % COLORS.length]}
                  />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </div>
        </div>
      </div>
      {/* 3. Sales Statistics */}
      <div className="section">
        <h2>판매 통계</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart
            data={dummyData.salesChartData}
            margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line
              type="monotone"
              dataKey="sales"
              stroke="#239edb"
              activeDot={{ r: 8 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="section-container">
        {/* 4. Maintenance History & Cost Analysis */}
        <div className="section">
          <h2>정비 비용 그래프</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart
              data={dummyData.maintenanceData}
              margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="cost" fill="#82ca9d" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* 5. Module & Option Popularity */}
        <div className="section">
          <h2>모듈 및 옵션 선호도</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart
              data={dummyData.moduleOptionPopularityData}
              margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="count" fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

export default MainDashboard;
