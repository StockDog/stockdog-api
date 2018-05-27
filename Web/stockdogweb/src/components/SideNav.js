import React, { Component } from 'react';
import { withCookies } from 'react-cookie';
import { withRouter } from "react-router-dom";
import API from "api";

import Logout from "./Logout";

class SideNav extends Component {
   constructor(props) {
      super(props);

      this.api = new API();
      this.cookies = this.props.cookies;

      this.state = {
         portfolios: [],
         elements: []
      };
   }

   componentDidMount() {
      this.api.getAllPortfolios(this.cookies.get("userId"), (data) => {
         this.setState({
            portfolios: data,
         });
         this.createSideNavElements();
      });

   }

   createSideNavElements = () => {
      var elements = [];

      this.state.portfolios.forEach((portfolio) => {
         elements.push(
            <div className="side-nav-element" key={portfolio.id} 
               onClick={()=> {this.switchToPortfolio(portfolio.id, 
                  portfolio["league"], portfolio["leagueId"])}}>
               <div className="side-nav-element-title">
                  <p>{portfolio["league"]}</p>
               </div>
               <div className="side-nav-element-value">
                  <p>$5000</p>
               </div>
            </div>
         );
      });

      this.setState({
         elements
      }); 
   }

   goToJoinLeague = () => {
      this.props.history.push("/join-league");
   };

   goToCreateLeague = () => {
      this.props.history.push("/create-league");
   };

   switchToPortfolio = (portfolioId, leagueName, leagueId) => {
      console.log("Switching to:");
      console.log(portfolioId);
      console.log(leagueName);
      console.log(leagueId);
      this.cookies.set("currPortfolio", portfolioId);
      this.cookies.set("currLeagueName", leagueName);
      this.cookies.set("currLeagueId", leagueId)
      this.cookies.get("currPortfolio");
      this.cookies.get("currLeagueName");
      this.cookies.get("currLeagueId");
      window.location.reload();
   };

   render() {
      return (
         <div className="SideNav">
            <div className="side-nav-btns">
               <button className="submit-btn side-nav-btn" id="league-advance"
                  onClick={this.goToJoinLeague}>
                  <span>Join</span></button>
               <button className="submit-btn side-nav-btn" id="league-advance"
                  onClick={this.goToCreateLeague}>
                  <span>Create</span></button>
            </div>
            {this.state.elements}
            <Logout />
         </div>
      );
   }
}

export default withRouter(withCookies(SideNav));