import React, { Component } from 'react';
import { StyleSheet, Text, TouchableOpacity, View, TextInput } from 'react-native';
import { Button } from 'react-native-elements';
import containers from '../style/containers';
import elements from '../style/elements';
import text from '../style/text';
import { colors } from '../style/colors.js'; 

export default class PortfolioItem extends Component {
  constructor(props) {
    super(props);
    this.state = {};
  }

  _onPress(ticker) {
    console.log(this.props);
    const navigate = this.props.navigation.navigate;
    navigate('Stock', {ticker: ticker});
  }

  render() {
    const numShares = 
      this.props.numShares ? 
        <Text style={text.smallPortfolioText}> {this.props.numShares} shares </Text> 
        : null;
    return (
      <View style={containers.portfolioItem}>
        <TouchableOpacity onPress={this._onPress.bind(this, this.props.ticker)}>
          <Text style={text.bigPortfolioText}> {this.props.ticker} </Text>
        </TouchableOpacity>
        {numShares}
        <Text style={text.bigPortfolioText}> ${this.props.price} </Text>
      </View>
    );
  }
};