import axiosInstance from "../axiosApi"

async function performExerciseLoading(id) {
  const response = await axiosInstance.get(`/v1/exercises/${id}/`)
  return response?.data
}

async function performExerciseSaving(id, data) {
  const response = await axiosInstance.put(`/v1/exercises/${id}/`, data)
  return response?.data
}

function getExercise(data) {
  return {
    type: 'LOAD_EXERCISE',
    payload: data
  }
}

function failedToLoad(error) {
  return {
    type: 'FAILED_TO_LOAD',
    payload: error
  }
}

function failedToSave(error) {
  return {
    type: 'FAILED_TO_SAVE',
    payload: error
  }
}

export function loadExercise(id) {
  return function (dispatch) {
    return performExerciseLoading(id).then(
      (data) => dispatch(getExercise(data)),
      (error) => dispatch(failedToLoad(error))
    )
  }
}

export function saveExercise(id, exercise) {
  return function (dispatch) {
    return performExerciseSaving(id, exercise).then(
      (data) => dispatch(getExercise(data)),
      (error) => dispatch(failedToSave(error))
    )
  }
}

export function loadTracks() {
  return function(dispatch) {
    return dispatch({
      type: 'LOAD_TRACKS',
      payload: axiosInstance.get('/v1/tracks/')
    })
  }
}
