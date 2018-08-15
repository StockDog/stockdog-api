import { StyleSheet } from 'react-native';
import { colors } from './colors.js'; 

export default text = StyleSheet.create({
    // ---------------- Tab Bar --------------- // 
    tabLabel: {
      color: colors.white, 
      fontSize: 12, 
      fontFamily: 'open-sans'
    },
    // ------------- Login/Register ----------- // 
    title: {
      color: colors.white,
      fontFamily: 'open-sans',
      fontSize: 40,
      backgroundColor: 'transparent'
    },
    loginButton: {
      fontSize: 20,
      fontFamily: 'open-sans',
      color: colors.white
    },
    smallText: {
      fontSize: 16,
      fontFamily: 'open-sans',
      color: colors.bright,
      textDecorationLine: 'underline'
    },
    // ---------------- Profile page ------------ //
    money: {
      color: colors.bright,
      fontFamily: 'open-sans',
      fontSize: 48,
      textAlign: 'center',
      paddingTop: 10
    },
    profileLabels: {
      color: colors.white,
      fontFamily: 'open-sans-bold',
      fontSize: 24,
      textAlign: 'left'
    },
    bigPortfolioText: {
      color: colors.white,
      fontFamily: 'open-sans',
      fontSize: 20,
      textAlign: 'left'
    },
    smallPortfolioText: {
      color: colors.white,
      fontFamily: 'open-sans',
      fontSize: 16,
      textAlign: 'left',
      paddingLeft: 20
    },
    // ----------------- Modals ------------- // 
    joinLeagueTitle: {
      color: colors.white,
      fontFamily: 'open-sans',
      fontSize: 24,
      textAlign: 'left'
    },
    joinLeagueWarning: {
      color: colors.white,
      fontFamily: 'open-sans',
      fontSize: 14,
      paddingTop: 10
    },
    modalHeader: {
      color: colors.white,
      fontFamily: 'open-sans',
      fontSize: 32
    },
    // ----------------- Stock page ------------- // 
    stock: {
      color: colors.bright,
      fontFamily: 'open-sans',
      fontSize: 36
    },
    stockMoney: {
      color: colors.bright,
      fontFamily: 'open-sans',
      fontSize: 42,
      textAlign: 'center'
    },
    // ----------------- Groups Drawer ------------- //
    groupTitle: {
      color: colors.dark,
      fontFamily: 'open-sans-bold',
      fontSize: 36,
      paddingLeft: 10
    },
    groupText: {
      color: colors.dark,
      fontFamily: 'open-sans',
      fontSize: 24,
      textAlign: 'left'
    },
    // ----------------- League Screen ------------- //
    leagueTitle: {
      color: colors.white,
      fontFamily: 'open-sans-bold',
      fontSize: 36,
    },
    inviteCode: {
      color: "gray",
      fontFamily: 'open-sans',
      fontSize: 20,
      textAlign: 'left',
    },
    members: {
      color: colors.white,
      fontFamily: 'open-sans',
      fontSize: 24
    },
    rank: {
      color: colors.white,
      fontFamily: 'open-sans',
      fontSize: 24
    },
    value: {
      color: colors.white,
      fontFamily: 'open-sans',
      fontSize: 24
    },
    addGroupText: {
      color: colors.dark,
      fontFamily: 'open-sans',
      fontSize: 20,
      textAlign: 'left'
    },
    code: {
      fontSize: 25,
      color: colors.white,
      fontFamily: 'open-sans',
      borderRadius: 0,
      borderColor: colors.bright,
      borderWidth: 2
    },
    // ----------------- Settings Modal ------------- //
    settingsTitle: {
      color: colors.white,
      fontFamily: 'open-sans',
      fontSize: 48, 
      textAlign: 'center',
    },
    // ----------------- Feed page ------------- //
    activityTitle: {
      color: colors.white
    },
    smallIconText: {
      fontSize: 16
    },
    medIconText: {
      fontSize: 14
    },
    largeIconText: {
      fontSize: 12
    },
    noActivity: {
      fontSize: 24,
      color: colors.white,
      textAlign: 'center'
    }
});