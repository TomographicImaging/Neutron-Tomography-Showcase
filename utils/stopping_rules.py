import numpy as np
from cil.optimisation.utilities import callbacks


class SharpnessCallback(callbacks.Callback):
    """
    Parameters
    ----------

    Properties
    ----------
    save_values: list of floats
      sharpness

    """

    def __init__(self, slicers_for_sharpness, threshold=0.25, min_iters=20):
        self.save_values={i:[] for i in range(len(slicers_for_sharpness))}
        self.slicers_for_sharpness = slicers_for_sharpness
        self.threshold = threshold
        self.min_iters = min_iters
        self.stabilised = [False for _ in range(len(slicers_for_sharpness))]
        self.num_same = [0 for _ in range(len(slicers_for_sharpness))]

    def __call__(self, algorithm):
        for k, slicer in enumerate(self.slicers_for_sharpness):
            calc_region = slicer(algorithm.get_output()).array
            sharpness = calculate_sharpness(calc_region)
            self.save_values[k].append(sharpness)
            if algorithm.iteration>0:
                if self.save_values[k][-1] == self.save_values[k][-2]:
                    self.num_same[k] += 1
                else:
                    self.num_same[k] = 0

            if (algorithm.iteration+1)>=self.min_iters:

                if self.num_same[k] >= self.threshold * (algorithm.iteration+1):
                    # print("Num same for slicer ", k, ": ", self.num_same[k])
                    # print("Threshold for slicer ", k, ": ", self.threshold * k)
                    # print(self.save_values[k])
                    self.stabilised[k] = True

        if all(self.stabilised):
            raise StopIteration
        

class SavingCallback(callbacks.Callback):
    """
    Parameters
    ----------

    Properties
    ----------
    saved_solutions: list
        List of solutions saved at each step.
    step: int
        The interval at which to save the solutions. For example, if step=10, the solution will be saved every 10 iterations.
    
        Methods
        -------
        __call__(algorithm)
            Saves the current solution of the algorithm at the specified intervals.

    """

    def __init__(self, step=1):
        self.saved_solutions = []
        self.step = step

    def __call__(self, algorithm):
        if algorithm.iteration % self.step == 0:
            self.saved_solutions.append(algorithm.solution.copy())


class SharpnessCallbackThreshold(callbacks.Callback):
    '''
    For each threshold determines stopping point based as the iteration at which the sharpness has not changed for the threshold percentage of iterations. 
    This is done for each slicer in slicers_for_sharpness. Once all slicers have stabilised, the stopping point is saved to threshold_values and the 
    solution is saved to threshold_solutions. Then the callback is reset and looks for the next threshold. 
    '''
    

    def __init__(self, slicers_for_sharpness, thresholds=[], min_iters=20):
        self.save_values={i:[] for i in range(len(slicers_for_sharpness))}
        self.slicers_for_sharpness = slicers_for_sharpness
        self.thresholds = thresholds
        self.min_iters = min_iters
        self.stabilised = [False for _ in range(len(slicers_for_sharpness))]
        self.num_same = [0 for _ in range(len(slicers_for_sharpness))]
        self.threshold_values = [0 for _ in range(len(self.thresholds))]
        self.threshold_solutions = []
        self.threshold_counter = 0

    def __call__(self, algorithm):
        for k, slicer in enumerate(self.slicers_for_sharpness):
            calc_region = slicer(algorithm.get_output()).array
            sharpness = calculate_sharpness(calc_region)
            self.save_values[k].append(sharpness)
            if algorithm.iteration>0:
                if self.save_values[k][-1] == self.save_values[k][-2]:
                    self.num_same[k] += 1
                else:
                    self.num_same[k] = 0

            if self.threshold_counter < len(self.thresholds):
                if (algorithm.iteration+1)>=self.min_iters:
                    if self.num_same[k] >= self.thresholds[self.threshold_counter] * (algorithm.iteration+1):
                        self.stabilised[k] = True

        if all(self.stabilised):
            self.threshold_values[self.threshold_counter] = algorithm.iteration
            self.threshold_solutions.append(algorithm.solution.copy())
            self.stabilised = [False for _ in range(len(self.slicers_for_sharpness))]
            self.threshold_counter += 1

        
def check_sharpness_stopping(sharpness_values, threshold=0.25, min_iters=20):
    count=0
    for i in range(len(sharpness_values)):
        if i>0:
            if sharpness_values[i] == sharpness_values[i-1]:
                count += 1
            else:
                count=0
        if (i+1)>=min_iters and count >= threshold * (i+1):
            return i, sharpness_values[i]
    return None

def check_sharpness_stopping_old(sharpness_values, threshold=0.25):
    for i in range(20, len(sharpness_values)):
        count = 0
        for j in range(i-1, -1, -1):
            if sharpness_values[j] == sharpness_values[i]:
                count += 1
            else:
                break
        if count >= threshold * i:
            return i, sharpness_values[i]
    return None

def calculate_sharpness(array1D):
    """Calculate the sharpness as the number of pixels taken to go from 10% to 90% of the maximum value"""
    # array_max = np.max(array1D)
    # array_min = np.min(array1D)
    # percent_10 = 0.1 * (array_max-array_min) + array_min
    # percent_90 = 0.9 * (array_max-array_min) + array_min
    # indices_above_10 = np.where(array1D >= percent_10)[0]
    # indices_above_90 = np.where(array1D >= percent_90)[0]
    # index_10 = indices_above_10[0]
    # index_90 = indices_above_90[0]
    # sharpness = index_90 - index_10

    # instead of using max and min, we can use the mean of the 10% and 90% values to be more robust to noise:
    # do mean of bottom 10% and top 10% of values:
    sorted_array = np.sort(array1D)
    num_values = len(sorted_array)
    mean_10 = np.mean(sorted_array[:int(0.1 * num_values)])
    mean_90 = np.mean(sorted_array[int(0.9 * num_values):])
    array_min = mean_10
    array_max = mean_90
    percent_10 = 0.1 * (array_max-array_min) + array_min
    percent_90 = 0.9 * (array_max-array_min) + array_min
    indices_above_10 = np.where(array1D >= percent_10)[0]
    indices_above_90 = np.where(array1D >= percent_90)[0]
    index_10 = indices_above_10[0]
    index_90 = indices_above_90[0]

    # print("indices above 10%:", indices_above_10)
    # print("indices above 90%:", indices_above_90)
    if np.isclose(index_10, index_90, atol=1):
        # then instead need to find the last index above 90% and the last index above 10%:
        index_90 = indices_above_90[-1]
        index_10 = indices_above_10[-1]
        sharpness2 = index_10 - index_90

    else:
        sharpness2 = index_90 - index_10
    return sharpness2