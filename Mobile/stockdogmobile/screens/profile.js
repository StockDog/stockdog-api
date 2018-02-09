import React, { Component } from 'react';
import { StyleSheet, Text, TouchableOpacity, View, FlatList, TextInput, DatePickerIOS } from 'react-native';
import { Button } from 'react-native-elements';
import containers from '../style/containers';
import elements from '../style/elements';
import text from '../style/text';
import { colors } from '../style/colors'; 
import ChartView from 'react-native-highcharts';
import Icon from 'react-native-vector-icons/Feather';

export default class Profile extends Component {
  constructor(props) {
    super(props);
    this.state = { 
      userId : "",
      data: [],
      isLoading: true
    };
  }

  componentDidMount() {
      
  }

  render() {
    return (
      <View style={containers.profileGeneral}>
        <View style={containers.iconHeaders}>
          <Icon name='user' size={30} color='white' />
          <Icon name='settings' size={30} color='white' />
        </View>
        <View style={containers.chart}>
            <Text style={text.money}>$20.05</Text>
        </View>
      </View>
    );
  }
}