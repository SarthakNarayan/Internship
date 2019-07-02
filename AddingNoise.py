import numpy as np
import matplotlib.pyplot as plt
import allantools

def reading_the_data(number = 305 , wanted ='X'):
    path_allan = r"C:\Users\Lenovo\Desktop\Internship\NoisyData" + "\\"  + str(wanted) + str(number) + ".npy"
    reading_the_data.save_path = r"C:\Users\Lenovo\Desktop\Internship\NoisyData" + "\\"  + str(wanted) + str(number)
    values = np.load(path_allan)
    print(values.shape)
    return values

def plotting(data1 , wanted = 'X' , save = 'yes'):
    rate = 20
    fig = plt.figure(figsize=(12,8))
    fig.subplots_adjust(hspace=0.5, wspace=0.2)
    x_axis = np.arange(1,(len(data1)+1),1)
    # Global title
    fig.suptitle("Allan Deviation for " + wanted + " with added noise with different standard deviation for rate " + str(rate))

    plt.subplot(3, 5, 1)
    plt.plot(x_axis , data1)
    plt.title(wanted + " coordinates vs frames without Noise")

    plt.subplot(3,5,3)
    tau , ad = allan_deviation(data1 , rate)
    plt.loglog(tau, ad,'b')
    plt.title('Allan Deviation Without Noise')

    counter = 6
    mean = 0
    for i in range(1,11,2):
        std = i*100
        
        noisy_signal = adding_noise(data1 , mean , std , seed = 23)

        plt.subplot(3,5,counter)
        tau , ad = allan_deviation(noisy_signal , rate)
        plt.loglog(tau, ad,'b' , label='Allan Deviation With Noise')
        plt.title("Std " + str(std))

        plt.subplot(3, 5, counter+1)
        plt.plot(x_axis , noisy_signal)
        plt.title("Std " + str(std))

        if counter < 16:
            counter += 2
        else:
            break

    plt.show()
    if save == 'yes':
        plot_path = reading_the_data.save_path + ".png"
        fig.savefig(plot_path)
    
def adding_noise(data , mean , std , seed = 23):
    np.random.seed(seed)
    uniform_distribution = np.random.randn(len(data))
    gaussian_noise = std*uniform_distribution + mean
    noisy_signal = data + gaussian_noise
    return noisy_signal

def allan_deviation(data , rate):
    tau1 = np.logspace(0, 4, 1000)  # tau values from 1 to 10000
    (tau2, ad, ade, adn) = allantools.oadev(data, rate=rate, data_type="freq", taus=tau1)
    return tau2,ad

def three_in_one(wanted = 'X' , save = 'yes'):
    path1 = r"C:\Users\Lenovo\Desktop\Internship\NoisyData" + "\\"  + str(wanted) + str(205) + ".npy"
    path2 = r"C:\Users\Lenovo\Desktop\Internship\NoisyData" + "\\"  + str(wanted) + str(305) + ".npy"
    path3 = r"C:\Users\Lenovo\Desktop\Internship\NoisyData" + "\\"  + str(wanted) + str(405) + ".npy"

    data1 = np.load(path1)
    data2 = np.load(path2)
    data3 = np.load(path3)

    tau1 = np.logspace(0, 4, 1000) 
    rate = [0.01,1,10,20,30,40,50,60,70,80,90,100]

    fig = plt.figure(figsize=(12,7)) #width , height
    fig.suptitle("Allan Deviation for " + wanted + " for different rates \n BLUE - 400 \n GREEN - 650 \n RED - 900")
    fig.subplots_adjust(hspace=0.9, wspace=0.8) #height , width

    for i,r in enumerate(rate):
        (tau21, ad1, ade, adn) = allantools.oadev(data1, rate=r, data_type="freq", taus=tau1)
        (tau22, ad2, ade, adn) = allantools.oadev(data2, rate=r, data_type="freq", taus=tau1)
        (tau23, ad3, ade, adn) = allantools.oadev(data3, rate=r, data_type="freq", taus=tau1)

        plt.subplot(3, 4, i+1)
        plt.loglog(tau21, ad1,'b')
        plt.loglog(tau22, ad2,'g')
        plt.loglog(tau23, ad3,'r')
        plt.title("Rate " + str(r))
        plt.xlabel('tau')
        plt.ylabel('ADEV [V]')
        plt.grid()

    plt.show()

    save_path = r"C:\Users\Lenovo\Desktop\Internship\NoisyData\\AllanAll" + wanted
    if save == 'yes':
        plot_path = save_path + ".png"
        fig.savefig(plot_path)

def main():
    # values = reading_the_data(205,'X')
    # plotting(values , 'X')
    three_in_one('Y' , 'yes')

if __name__ == '__main__':
    main()