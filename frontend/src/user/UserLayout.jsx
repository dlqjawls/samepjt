import React from "react";
import Navbar from "../common/navigationBar";
import Footer from "../common/footer";
import { Outlet } from "react-router-dom";
import "./UserLayout.css";

const UserLayout = () => {
  return (
    <>
      <Navbar />
      <main className="user-content">
        <Outlet />
      </main>
      <Footer />
    </>
  );
};

export default UserLayout;
