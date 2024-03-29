// function to randomise(shuffle) an array
function shuffle(array) {
    var currentIndex = array.length,  randomIndex;
    while (currentIndex != 0) {
        randomIndex = Math.floor(Math.random() * currentIndex);
        currentIndex--;
        [array[currentIndex], array[randomIndex]] = [array[randomIndex], array[currentIndex]];
    }
    return array;
}


// Creating and shuffling factor array
var factors = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];
shuffle(factors);

// Initialising other global variables
var question_number = 0;
var num_of_corr_answers = 0;
var game_started = false;
var timePassed = 0;
var timeRemaining = 3000;   
var startTime;     
var wrong_questions = [];
var medal_earned = 0;

function resetVariables() {
    shuffle(factors);
    medal_earned = 0;
    question_number = 0;
    num_of_corr_answers = 0;
    wrong_questions = [tt]; //emptying wrong_questions except for tt
}

function resetStartButton() {
    // Disabling answer text box, displaying start button
    document.querySelector('#answer').disabled = true;
    document.querySelector('#answer').style.backgroundImage = "url('/static/images/answerbox_inactive.png')";
    document.querySelector('#main_button').style.display = 'block';
    document.querySelector('#main_button').innerHTML = 'Play Again';
}

function create_question() {
    
    // Changing font size
    document.querySelector('#text').style.fontSize = '3em';

    // Displaying question
    document.querySelector('#text').innerHTML = factors[question_number] + ' x ' + tt;

    // Playing sound
    var questionsound = new Audio('/static/sounds/' + factors[question_number] + 'x' + tt + '.mp3');
    questionsound.play();

    var corr_answer = factors[question_number] * tt;
    return corr_answer;
}

// This function is called 2000ms after the tick or cross are displayed, to hide them again.
function right_wrong_timeout() {
    document.querySelector('#right_wrong').style.display = 'none';
}

function check_answer(corr_answer) {
    var answer = document.querySelector('#answer').value;
    if (answer.length >= String(corr_answer).length)
    {
        // Answer is correct
        if (answer == corr_answer) {
            // Displaying checkmark
            document.querySelector('#right_wrong').src = '/static/images/tick.png';
            document.querySelector('#right_wrong').style.display = 'block';

            // Checking if a timer has been started and clearing it first before starting a new one
            if (typeof right_wrong_timer !== 'undefined') { 
                clearInterval(right_wrong_timer);
            }
            right_wrong_timer = setTimeout(right_wrong_timeout, 2000);
            num_of_corr_answers++;

            // Displaying in progress bar
            if (question_number == 0) {
                document.querySelector('#progress' + question_number).src="/static/images/counter1_corr.png";
            }
            else if (question_number == 11) {
                document.querySelector('#progress' + question_number).src="/static/images/counter_last_corr.png";
            }
            else {
                document.querySelector('#progress' + question_number).src="/static/images/counter_mid_corr.png";
            }
            
        }

        // Answer is wrong
        else { 
            wrong_questions.push(factors[question_number]);
            document.querySelector('#right_wrong').src = '/static/images/cross.png';
            document.querySelector('#right_wrong').style.display = 'block';
            if (typeof right_wrong_timer !== 'undefined') {
                clearInterval(right_wrong_timer);
            }
            right_wrong_timer = setTimeout(right_wrong_timeout, 2000);
            
            // Displaying in progress bar
            if (question_number == 0) {
                document.querySelector('#progress' + question_number).src="/static/images/counter1_wrong.png";
            }
            else if (question_number == 11) {
                document.querySelector('#progress' + question_number).src="/static/images/counter_last_wrong.png";
            }
            else {
                document.querySelector('#progress' + question_number).src="/static/images/counter_mid_wrong.png";
            }
        }

        // Activating next question on progress bar
        if (question_number == 10) {
            document.querySelector('#progress11').src="/static/images/counter_last_active.png";
        }
        else if (question_number < 10) {
            document.querySelector('#progress' + (question_number + 1)).src="/static/images/counter_mid_active.png";
        }
        
        return true;    // So we know an answer has been checked          
    }
}

function displayFinalMessage(fontSize, message, imagePath, medal) {
  document.querySelector('#text').style.fontSize = fontSize;
  document.querySelector('#text').innerHTML = message;                
  document.querySelector('#medalpic').src = imagePath;
  document.querySelector('#display').style.display = 'block';
  document.querySelector('#medalpic').style.display = 'block';
  medal_earned = medal;
}

function sendMedalResult(medal, timeAchieved=0) {
    var data = new FormData();
    data.append('medal_earned', medal);
    if (timeAchieved > 0) {
        data.append('time_achieved', timeAchieved);
    }  
    var request = new XMLHttpRequest();
    request.open('POST', '/test/' + tt);
    request.send(data);
}

function finish() {
    game_started = false;
    // Checking if the last question was answered or time ran out (in which case it counts as wrong)
    if (question_number == 11 && timeRemaining == 0) {
        wrong_questions.push(factors[question_number]);
    }
    // Checking penultimate question
    else if (question_number == 10 && timeRemaining == 0) {
        wrong_questions.push(factors[question_number]);
        question_number++;
        wrong_questions.push(factors[question_number]);
    }
    
    // Displaying final messages
    
    // gold
    if (num_of_corr_answers > 11 && timeRemaining > 499) {
      displayFinalMessage('1.15em', '<br><br>Congratulations.<br>You earned a gold medal!', '/static/images/gold.png', 3);
      sendMedalResult(3, timePassed);
    }
    // silver
    else if (num_of_corr_answers > 11) {
      displayFinalMessage('1.15em', '<br>Congratulations.<br>You earned a silver medal!', '/static/images/silver.png', 2);
      sendMedalResult(2);
    }
    // bronze - too slow
    else if (num_of_corr_answers > 9 && timeRemaining == 0) {
      displayFinalMessage('1em', '<br>Congratulations.<br>You earned a bronze medal.<br>Keep on practising<br>to get faster.', '/static/images/bronze.png', 1);
      sendMedalResult(1);
    }
    // bronze - 1 question wrong
    else if (num_of_corr_answers > 10) {
      displayFinalMessage('0.8em', '<br>Congratulations.<br>You earned a bronze medal.<br>Revise this question:<br>' + wrong_questions[1] + ' x ' + tt + ' = ' + wrong_questions[1]*tt, '/static/images/bronze.png', 1);
      sendMedalResult(1);
    }
    // bronze - 2 questions wrong
    else if (num_of_corr_answers > 9) {
      displayFinalMessage('0.8em', '<br>Congratulations.<br>You earned a bronze medal.<br>Revise these questions:<br>' + wrong_questions[1] + ' x ' + tt + ' = ' + wrong_questions[1]*tt + '<br>' + wrong_questions[2] + ' x ' + tt + ' = ' + wrong_questions[2]*tt, '/static/images/bronze.png', 1);
      sendMedalResult(1);
    }
    // no medal
    else {
        document.querySelector('#text').style.fontSize = '1em';
        document.querySelector('#text').innerHTML = 'You got ' + num_of_corr_answers + ' out of 12 answers correct.<br>Keep on practising.';
    }

    resetStartButton();    
    resetVariables();
}

// Called whenever the page is redrawn via requestAnimationFrame
const changeTimer = () => {
    if (game_started == true) {

    // Shrinking the timer bar
    document.querySelector('#timerbar').style.height = (initial_height / 3000 * (timeRemaining)) + 'px';
    document.querySelector('#timerbar').style.top = (initial_top + (initial_height / 3000 * (3000 - timeRemaining))) + 'px';

        let currentTime = new Date().getTime();
        timePassed = Math.floor((currentTime - startTime) / 10);
        timeRemaining = 3000 - timePassed;

        let timeDisplayed = document.querySelector('#timer');

        if (timePassed < 3000) {
            let seconds = Math.floor(timePassed / 100)
            let hundredths = timePassed - (seconds * 100)
            if (hundredths < 10) {
                hundredths = '0' + hundredths
            }
            if (timePassed > 999) {
                timeDisplayed.innerHTML = `${seconds}:${hundredths}`;
            }
            else if (timePassed > 99) {
            timeDisplayed.innerHTML = `0${seconds}:${hundredths}`;
            }
            else if (timePassed > 9) {
            timeDisplayed.innerHTML = `00:${hundredths}`;
            }
        }
        else {
            timePassed = 3000;
            timeDisplayed.innerHTML = '30:00';
            finish();
        }

        window.requestAnimationFrame(changeTimer);
    } 
}

// When the site is loaded
document.addEventListener('DOMContentLoaded', function() {

    // Declaring global tt variable (passed into html with jinja)
    tt = parseInt(document.querySelector('#tt').innerHTML);
    
    // Adding the timestable to the wrong answers array, so we know later which tt the factors refer to.
    wrong_questions.push(tt); 

    // Needed to calculate timer bar, if in different screen sizes
    initial_height = document.querySelector('#timerbar').offsetHeight;
    initial_top = document.querySelector('#timerbar').offsetTop; 
    
    // Disabling answer text box
    document.querySelector('#answer').disabled = true;

    // Hiding tick and cross (rightwrong)
    document.querySelector('#right_wrong').style.display = "none";

    // When a key is pressed
    document.querySelector('#answer').addEventListener('keyup', function() {
        if (game_started) {
            // checking answer, returning true if it has been checked
            if (check_answer(corr_answer)) {
                document.querySelector('#answer').value = '';
                
                console.log(question_number);

                if (question_number < 11) {
                    question_number++;
                    corr_answer = create_question();
                    document.querySelector('#answer').focus();
                }
                else {                            
                    finish();
                }
            }
        }    

    });

    // When main button is clicked
    document.querySelector('#main_button').addEventListener('click', function() {
        // Game gets started
        game_started = true;

        //Hiding main button, enabling & focusing answer box
        document.querySelector('#main_button').style.display = 'none';
        let answerBox = document.querySelector('#answer')
        answerBox.disabled = false;
        answerBox.focus();
        answerBox.style.backgroundImage = "url('/static/images/answerbox.png')";
        
        // Hiding medal picture
        document.querySelector('#medalpic').style.display = 'none';
        document.querySelector('#display').style.display = 'flex';

        // Activating and emptying progress bar
        document.querySelector('#progress0').src="/static/images/counter1_active.png";
        document.querySelector('#progress11').src="/static/images/counter_last.png";
        for (var i = 1; i < 11; i++) {
            document.querySelector('#progress' + i).src="/static/images/counter_mid.png";
        }               
        
        // Starting timer
        document.querySelector('#timer').innerHTML = '30:00';
        timeRemaining = 3000;
        startTime = new Date().getTime();
        window.requestAnimationFrame(changeTimer);

        // Create first question
        corr_answer = create_question();
    });
});