import allantools
import matplotlib.pyplot as plt
import numpy as np

def allandeviation(density = 'low' , wanted = "X" , number = 0,save = 'yes'):
    if density == 'low':
        if wanted == "X":
            path_allan = r"C:\Users\Lenovo\Desktop\Internship\Data\LessDense" + "\X" + str(number) + ".npy" 
            save_path = r"C:\Users\Lenovo\Desktop\Internship\Data\LessDense" + "\Xallan" + str(number)
        if wanted == "Y":  
            path_allan = r"C:\Users\Lenovo\Desktop\Internship\Data\LessDense" + "\Y" + str(number) + ".npy"
            save_path = r"C:\Users\Lenovo\Desktop\Internship\Data\LessDense" + "\Yallan" + str(number)
    if density == 'high':
        if wanted == "X":
            path_allan = r"C:\Users\Lenovo\Desktop\Internship\Data\MoreDense" + "\X" + str(number) + ".npy" 
            save_path = r"C:\Users\Lenovo\Desktop\Internship\Data\MoreDense" + "\Xallan" + str(number)
        if wanted == "Y":  
            path_allan =  r"C:\Users\Lenovo\Desktop\Internship\Data\MoreDense" + "\Y" + str(number) + ".npy"
            save_path = r"C:\Users\Lenovo\Desktop\Internship\Data\MoreDense" + "\Yallan" + str(number)
    if density == 'random':
        wanted = "Random"
        save_path = r"C:\Users\Lenovo\Desktop\Internship\Data\allanRandom" + str(number)

    values = np.load(path_allan)
    # tau = []
    # for i in range(1,(len(values)+1)):
    #     tau.append(i)

    tau1 = np.logspace(0, 4, 1000)  # tau values from 1 to 10000

    # values = np.random.randn(10000)
    
    rate = [0.01,1,10,20,30,40,50,60,70,80,90,100]

    fig = plt.figure(figsize=(12,6)) #width , height
    # Global title
    fig.suptitle("Allan Deviation for " + wanted + " for different rates")
    for i,r in enumerate(rate):
        (tau2, ad, ade, adn) = allantools.oadev(values, rate=r, data_type="freq", taus=tau1)
        fig.subplots_adjust(hspace=0.8, wspace=0.8) #height , width
        plt.subplot(3, 4, i+1)
        plt.loglog(tau2, ad,'b')
        plt.title("Rate " + str(r))
        plt.xlabel('tau')
        plt.ylabel('ADEV [V]')
        plt.grid()

        # Calculating the characteristics
        characteristics_calculation(tau2, ad, ade, adn , r)
    plt.show()

    if save == 'yes':
        plot_path = save_path + ".png"
        fig.savefig(plot_path)

def characteristics_calculation(tau , ad , ade , adn , r):
    idx_min = np.argmin(ad)
    idx_max = np.argmax(ad)
    allandeviation_minimum_value = ad[idx_min] 
    allandeviation_maximum_value = ad[idx_max]
    tau_min = tau[idx_min]
    tau_max = tau[idx_max]

    print("--------------------------------------------------------------------------------")
    print("For rate " + str(r))
    # print("The index of the lowest value ",idx_min)
    # print("The index of the highest value ",idx_max)
    print("The lowest value for allan deviation",allandeviation_minimum_value)
    print("The maximum value for allan deviation",allandeviation_maximum_value)
    print("The tau at which lowest value occurs ",tau_min)
    print("The tau at which maximum value occurs ",tau_max)
    # print ('Bias stability is '+str(allandeviation_minimum_value)+'V at '+str(tau_min)+'s of averaging time.')

    t21_ind1 = np.where(tau==1.0) # index of array t2 where the value is 1s.
    noise = ad[t21_ind1[0]]
    # noise density is value of ADEV curve at 1s averaging time.
    print('Noise spectral density is '+str(noise))
    # print('Allan deviation erros {}'.format(ade))
    # print('Values of N used in calculation {}'.format(adn))
def main():
    allandeviation('low','Y',105,'no')

if __name__ == '__main__':
    main()

