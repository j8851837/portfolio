'use strict';

const tweetElement = {};
const tweetsList = [];
const windowHeight = window.innerHeight; 
const divIdTweets = document.getElementById('tweets');
let twitterApiRunning = true;
let loading;
let fifthFromLowerTweetElement;
let windowActive;


const sortResponseTweets = (response) => {
    const responseTweets = response['timeline'];
    const keys = Object.keys(responseTweets);
    keys.sort().reverse();
    const responseTweetsSorted = {};
    for(const key of keys) {
        responseTweetsSorted[key] = responseTweets[key];
    };
    return responseTweetsSorted;
};


const createClassTweet = (tweetId, responseTweetsSorted) => {
    const userNameResponse = responseTweetsSorted[tweetId]['user'];
    const maxLengthName = 20;
    const userName = (userNameResponse.length < maxLengthName
        ? userNameResponse
        : userNameResponse.substr(0, maxLengthName) + '...'
    )
    const isFavorited = () => {
        if (responseTweetsSorted[tweetId]['favorited']===false) {
            return '<span style="color:#af1c1c">♡</span>'
        } else {
            return '<span style="color:#af1c1c">♥</span>';
        }
    }
    const htmlElement = `<div class='tweet' id=${tweetId}>
                            <a class ='link_official_site' href='https://twitter.com/kuma_jaguar/status/${[tweetId]}'></a>
                            <div class='tweet_body'>
                            <div class='name_time_fav'>
                                    <div class='name_time'>
                                        <div class='name'>${userName}</div>
                                        <div class='time'>${responseTweetsSorted[tweetId]['time']}</div>
                                    </div>
                                    <div class='is_favorited' id=${'fav'+tweetId} onclick='favClick("${[tweetId]}");'>${isFavorited()}</div>
                                </div>
                                <div class='text'>
                                    ${responseTweetsSorted[tweetId]['text']}
                                </div>
                            </div>
                        </div>`;
    return htmlElement;
};


const scrollToTopTweet = (topTweetId) => {
    const lastDisplay = document.getElementById(topTweetId);
    lastDisplay.scrollIntoView({});
};


const insertApiErrorMassage = () => {
    {
        const errorMassage = document.createElement('div');
        errorMassage.append('Twitter API Error 時間をおいてアクセスしてください。');
        errorMassage.setAttribute('class', 'error');
        divIdTweets.prepend(errorMassage);
    }
    {
        const errorMassage = document.createElement('div');
        errorMassage.append('Twitter API Error 時間をおいてアクセスしてください。');
        errorMassage.setAttribute('class', 'error');
        console.log(errorMassage)
        divIdTweets.appendChild(errorMassage);
    }
}


const loadTweets = async (url) => {
    loading = true;
    try {
        const response = await fetch(url, {credentials: 'include'});
        const responseJson = await response.json();
        if ('timeline' in responseJson) {
            const responseTweetsSorted = sortResponseTweets(responseJson);
            for (const tweetId in responseTweetsSorted) {
                const classTweet = createClassTweet(tweetId, responseTweetsSorted);
                divIdTweets.insertAdjacentHTML('beforeend', classTweet);
                tweetElement[tweetId] = document.getElementById(tweetId);
                tweetsList.push(tweetId);
            };
            tweetsList.sort();
            fifthFromLowerTweetElement = tweetElement[tweetsList[4]];
            if ('topTweet' in responseJson) {
                scrollToTopTweet(responseJson['topTweet']);
            };
        };
        if ('Twitter API Error' in responseJson) {
            twitterApiRunning = false;
            insertApiErrorMassage();
        };

    }
    catch (e) {
        console.log('通信エラー');
    }
    loading = false;    
};


window.addEventListener('load', () => {
    loadTweets('./timeline');
});


const loadPastTweets = () => {
    const params = {'bottomTweetId': tweetsList[0]};
    const query_params = new URLSearchParams(params);
    loadTweets(`./past_tweets?${query_params}`);
};


const displayLike = (tweetId, character, styleColor ,onClick) => {
    const favElement = document.getElementById(`fav${tweetId}`);
    const likeCharacter = document.createElement('div');
    likeCharacter.append(character);
    likeCharacter.setAttribute('class', 'is_favorited');
    likeCharacter.setAttribute('id', `fav${tweetId}`);
    if (onClick) {
        likeCharacter.setAttribute('onclick', `favClick('${[tweetId]}')`);
    };
    likeCharacter.setAttribute('style', styleColor);
    favElement.replaceWith(likeCharacter);
};


const favClick = async (tweetId) => {
    displayLike(tweetId, '♥', 'color:#2b2c34', false);
    const params = {'id_to_like' : tweetId};
    const query_params = new URLSearchParams(params);
    try {
        const response = await fetch(`./set_like?${query_params}`, {credentials: 'include'});
        const responseJson = await response.json();
        if (responseJson['result_set_like']) {
            displayLike(tweetId, '♥', 'color:#af1c1c', true);
        } else {
            displayLike(tweetId, '♡', 'color:#af1c1c', true);
        };
    }
    catch (e) {
        console.log('通信エラー');
    }
};


const seekTopTweet = () => {
    const tweetTopDisplayed = {'height':9999};
    for (const tweetId in tweetElement) {
        const tweetPosition = tweetElement[tweetId].getBoundingClientRect().top;
        if (tweetPosition>0 && tweetPosition<tweetTopDisplayed['height']) {
            tweetTopDisplayed['id'] = tweetId;
            tweetTopDisplayed['height'] = tweetPosition;
        };
    };
    return tweetTopDisplayed['id'];
};


const sendReadingPositionToServer = async () => {
    const topDisplayedTweetId = seekTopTweet();
    const indexOfTopTweet = tweetsList.indexOf(topDisplayedTweetId);
    const indexOf30thTweet = indexOfTopTweet-30;
    const tweet30th = (
        indexOf30thTweet >= 0 
        ? tweetsList[indexOf30thTweet] 
        : tweetsList[0]
    )
    const needs_get_api = (
        indexOfTopTweet > tweetsList.length-30
        ? 'True'
        : 'False'
    )
    const params = {
        'top_tweet' : topDisplayedTweetId,
        'tweet_30th' : tweet30th,
        'needs_get_api' : needs_get_api,
    };
    console.log(params);
    const query_params = new URLSearchParams(params);
    try {
        const response = await fetch(`./set_reading_position?${query_params}`, {credentials: 'include'});
        const responseJson = await response.json();
        console.log(responseJson['result']);
    }
    catch (e) {
        console.log('通信エラー');
    }

    if (document.hasFocus!==true) {
        windowActive = false;
    };
    
};


setInterval(() => {
    if (document.hasFocus()) {
        windowActive = true;
    };
    if (
        windowHeight > fifthFromLowerTweetElement.getBoundingClientRect().top 
        && loading === false 
        && twitterApiRunning === true
        ) { 
            loadPastTweets();
        };
}, 1000);


setInterval(() => {
    if (windowActive === true) {
        sendReadingPositionToServer();
    }
}, 5000);
