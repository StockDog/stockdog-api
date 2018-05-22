import React, { Component } from 'react';
import { StyleSheet, Text, TouchableOpacity, View, TextInput, Button } from 'react-native';
import Lightbox from '../components/baseLightbox';
import DatePicker from 'react-native-datepicker';
import { Actions } from 'react-native-router-flux';
import containers from '../style/containers';
import elements from '../style/elements';
import text from '../style/text';
import Modal from 'react-native-modal';
import RoundInput from '../components/roundinput';
import WideButton from '../components/widebutton';
import Icon from 'react-native-vector-icons/Feather';
import Api from '../api';

export default class AddPortfolioModal extends Component {
  constructor(props) {
    super(props);    
    this.state = {
      name: "",
      buyPower: "",
      startDate: "",
      endDate: "",
      minDate: "2001-01-01"
    };

    this.api = new Api();
  }

  componentDidMount() {
    this.setState({minDate: this.getCurrDate()});
  }

  getCurrDate = () => {
    var today = new Date();
    var dd = today.getDate();
    var mm = today.getMonth()+1; //January is 0!
    var yyyy = today.getFullYear();  // Last 2 digits of the date
    
    if(dd<10) {
        dd = '0'+dd
    } 
    
    if(mm<10) {
        mm = '0'+mm
    } 
    
    today = yyyy + '-' + mm + '-' + dd;
    return today;
  }

  onpress = () => {
    if (/[a-zA-Z]/.test(this.state.buyPower)) {
      alert("Invalid buypower value. Please enter numbers only.");
    }
    else if (this.state.startDate && this.state.endDate && 
      (this.state.startDate >= this.state.endDate)) {
        alert("Invalid dates. Please make the end date later than the start date.");
      }
    else {
      Actions.setnickname(this.state);
    }
  }

  close = () => {
    Actions.pop();
  };

  render() {
    var disabled = !(this.state.name && 
      this.state.buyPower && 
      this.state.startDate && 
      this.state.endDate)

    return (
        <Lightbox verticalPercent={0.7} horizontalPercent={0.8}>
          <View style={containers.addGroupOuterModal}>
            <View style={containers.addGroupModalHeader}>
              <Text style={text.modalHeader}> Create a League </Text>
              <TouchableOpacity onPress={this.close}>
                <Icon name='x' size={30} color='white' />
              </TouchableOpacity>
            </View>
            <View style={containers.addGroupInnerModal}>
             <RoundInput 
                type="Name" 
                onchange={(name) => this.setState({name})} 
                value={this.state.name}/>
              <RoundInput 
                type="Buying Power" 
                onchange={(buyPower) => this.setState({buyPower})} 
                value={this.state.buyPower}/>
              <DatePicker
                style={elements.roundedInput}
                date={this.state.startDate}
                mode="date"
                placeholder="Select start date"
                format="YYYY-MM-DD"
                minDate={this.state.minDate}
                confirmBtnText="Confirm"
                cancelBtnText="Cancel"
                customStyles={{
                  placeholderText: {
                    fontFamily: 'open-sans',
                    textAlign: 'left',
                    color: "#aaaaaa",
                    marginLeft: -30
                  },
                  dateInput: {
                    flex: 0.7,
                    alignItems: 'flex-start',
                    borderWidth: 0
                  }
                }}
                iconComponent={<Icon name='calendar' size={30} color='grey' />}
                onDateChange={(startDate) => {this.setState({startDate})}}
              />
              <DatePicker
                style={elements.roundedInput}
                date={this.state.endDate}
                mode="date"
                placeholder="Select end date"
                format="YYYY-MM-DD"
                minDate={this.state.minDate}
                confirmBtnText="Confirm"
                cancelBtnText="Cancel"
                customStyles={{
                  placeholderText: {
                    fontFamily: 'open-sans',
                    textAlign: 'left',
                    color: "#aaaaaa",
                    marginLeft: -30
                  },
                  dateInput: {
                    flex: 0.7,
                    alignItems: 'flex-start',
                    borderWidth: 0
                  }
                }}
                iconComponent={<Icon name='calendar' size={30} color='grey' />}
                onDateChange={(endDate) => {this.setState({endDate})}}
              />
              <WideButton disabled={disabled} type="portfolio" onpress = {this.onpress}/>
            </View>
          </View>
        </Lightbox>
    );
  }
};
