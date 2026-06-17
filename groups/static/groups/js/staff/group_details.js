const questionModal = document.getElementById("questionModal")

questionModal.addEventListener("show.bs.modal", function (event){
    const button = event.relatedTarget

    const number = button.getAttribute('data-qnumber')
    const difficulty = button.getAttribute('data-qdifficulty')
    const prompt = button.getAttribute('data-qprompt')
    const answer = button.getAttribute('data-qanswer')
    const ganswer = button.getAttribute('data-ganswer')

    document.getElementById('modal-title').textContent = `${number} - ${difficulty}`
    document.getElementById('modal-prompt').textContent = prompt
    document.getElementById('modal-answer').textContent = answer
    document.getElementById('modal-groupAnswer').textContent = ganswer

})