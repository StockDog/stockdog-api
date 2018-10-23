import { ActionConst } from 'react-native-router-flux';
import { combineReducers } from 'redux';

// import the other reducers
import loginReducer from './loginReducer';

const sceneReducer = (state = {}, {type, scene}) => {
    switch(type){
        case ActionConst.FOCUS:
            return { ...state, scene };
        default:
            return state;
    }    
}


export default reducers = combineReducers({
    sceneReducer,
    loginReducer,
});