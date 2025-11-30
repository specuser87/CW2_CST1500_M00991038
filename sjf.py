#sjf.py (shortest job first)
# Shortest Job First - Scheduling
#Author: Babafemi Ajayi, M00991038

"""
Shortest Job First (SJF) Process Scheduler with Threading
Demonstrates concurrent execution simulation and proper thread synchronization.
"""

import threading
import time
from typing import List, Tuple
from dataclasses import dataclass, field


@dataclass
class Process:
    """
    Represents a process with scheduling metrics.
    
    Attributes:
        pid: Process identifier (unique integer)
        burst_time: CPU time required by the process
        waiting_time: Time spent waiting in ready queue
        turnaround_time: Total time from arrival to completion
        arrival_time: Time when process enters the system (for advanced scenarios)
        completion_time: Time when process finishes execution
    """
    pid: int
    burst_time: int
    waiting_time: int = 0
    turnaround_time: int = 0
    arrival_time: int = 0
    completion_time: int = 0
    
    def __repr__(self) -> str:
        """String representation for debugging purposes."""
        return (f"Process(pid={self.pid}, burst={self.burst_time}, "
                f"wait={self.waiting_time}, turnaround={self.turnaround_time})")


class ProcessInputHandler:
    """
    Handles user input for process creation with validation.
    Demonstrates separation of concerns and input validation best practices.
    """
    
    @staticmethod
    def validate_positive_int(prompt: str, error_msg: str = "Must be positive integer") -> int:
        """
        Validates and returns a positive integer from user input.
        
        Args:
            prompt: Message displayed to user
            error_msg: Custom error message for invalid input
            
        Returns:
            Validated positive integer
        """
        while True:
            try:
                value = int(input(prompt))
                if value <= 0:
                    print(f"Error: {error_msg}")
                    continue
                return value
            except ValueError:
                print(f"Error: Invalid input. {error_msg}")
    
    def input_processes(self) -> List[Process]:
        """
        Collects process information from user with robust error handling.
        
        Returns:
            List of Process objects with user-defined burst times
        """
        processes = []
        n = self.validate_positive_int(
            "Enter number of processes: ",
            "Number of processes must be a positive integer"
        )
        
        print(f"\n{'='*50}")
        print("Enter burst times for each process")
        print(f"{'='*50}")
        
        for i in range(1, n + 1):
            burst = self.validate_positive_int(
                f"Process {i} - Burst time: ",
                "Burst time must be a positive integer"
            )
            processes.append(Process(pid=i, burst_time=burst))
        
        return processes


class SJFScheduler:
    """
    Implements Shortest Job First (SJF) scheduling algorithm.
    Uses threading to simulate concurrent process execution.
    """
    
    def __init__(self, processes: List[Process]):
        """
        Initialize scheduler with process list.
        
        Args:
            processes: List of Process objects to schedule
        """
        self.processes = processes
        self.lock = threading.Lock()  # Ensures thread-safe operations
        self.completed_processes = []  # Tracks execution order
        
    def calculate_metrics(self) -> List[Process]:
        """
        Calculate waiting time and turnaround time for each process.
        Uses SJF (non-preemptive) algorithm.
        
        Algorithm:
        1. Sort processes by burst time (shortest first)
        2. First process: waiting_time = 0
        3. Subsequent processes: waiting_time = previous_completion_time
        4. turnaround_time = waiting_time + burst_time
        
        Returns:
            Sorted list of processes with calculated metrics
        """
        # Sort by burst time - core of SJF algorithm
        self.processes.sort(key=lambda p: p.burst_time)
        
        current_time = 0
        
        for process in self.processes:
            # Waiting time is the current time (when process starts)
            process.waiting_time = current_time
            
            # Turnaround time = waiting + execution
            process.turnaround_time = process.waiting_time + process.burst_time
            
            # Completion time for next process calculation
            process.completion_time = current_time + process.burst_time
            
            # Update current time for next process
            current_time = process.completion_time
        
        return self.processes
    
    def simulate_execution(self, process: Process, execution_speed: float = 0.1) -> None:
        """
        Simulates process execution using threading with visual feedback.
        Thread-safe operation using locks for shared resource access.
        
        Args:
            process: Process object to execute
            execution_speed: Time multiplier for simulation (seconds per burst unit)
        """
        # Simulate execution time (scaled down for demonstration)
        execution_time = process.burst_time * execution_speed
        
        with self.lock:  # Thread-safe console output
            print(f"\n[THREAD-{threading.current_thread().name}] "
                  f"Executing Process {process.pid} "
                  f"(Burst Time: {process.burst_time})")
        
        # Simulate CPU burst with progress indication
        time.sleep(execution_time)
        
        with self.lock:  # Thread-safe list modification
            self.completed_processes.append(process)
            print(f"[THREAD-{threading.current_thread().name}] "
                  f"Process {process.pid} completed")
    
    def run_threaded_simulation(self, execution_speed: float = 0.1) -> None:
        """
        Creates and manages threads to simulate concurrent process execution.
        Demonstrates proper thread lifecycle management.
        
        Args:
            execution_speed: Simulation speed multiplier
        """
        threads: List[threading.Thread] = []
        
        print(f"\n{'='*60}")
        print("STARTING THREADED EXECUTION SIMULATION")
        print(f"{'='*60}")
        
        # Create thread for each process
        for process in self.processes:
            thread = threading.Thread(
                target=self.simulate_execution,
                args=(process, execution_speed),
                name=f"P{process.pid}"  # Meaningful thread names
            )
            threads.append(thread)
            thread.start()  # Begin execution
        
        # Wait for all threads to complete (join pattern)
        for thread in threads:
            thread.join()
        
        print(f"\n{'='*60}")
        print("ALL PROCESSES COMPLETED")
        print(f"{'='*60}")


class OutputFormatter:
    """
    Handles formatted output display with statistical calculations.
    Demonstrates separation of presentation logic.
    """
    
    @staticmethod
    def print_results(processes: List[Process]) -> None:
        """
        Display scheduling results in formatted table with statistics.
        
        Args:
            processes: List of scheduled processes with calculated metrics
        """
        print(f"\n{'='*70}")
        print("SHORTEST JOB FIRST (SJF) SCHEDULING RESULTS")
        print(f"{'='*70}")
        
        # Table header
        header = f"{'PID':<8}{'Burst Time':<15}{'Waiting Time':<18}{'Turnaround Time':<18}"
        print(header)
        print('-' * 70)
        
        # Accumulate totals for average calculation
        total_wait = 0
        total_turnaround = 0
        
        # Display each process
        for p in processes:
            print(f"{p.pid:<8}{p.burst_time:<15}{p.waiting_time:<18}{p.turnaround_time:<18}")
            total_wait += p.waiting_time
            total_turnaround += p.turnaround_time
        
        print('-' * 70)
        
        # Calculate and display averages
        n = len(processes)
        avg_wait = total_wait / n
        avg_turnaround = total_turnaround / n
        
        print(f"\n{'PERFORMANCE METRICS':^70}")
        print(f"{'='*70}")
        print(f"Total Processes:           {n}")
        print(f"Average Waiting Time:      {avg_wait:.2f} time units")
        print(f"Average Turnaround Time:   {avg_turnaround:.2f} time units")
        print(f"{'='*70}\n")


def main() -> None:
    """
    Main execution flow demonstrating OOP principles and threading.
    Orchestrates the entire scheduling simulation.
    """
    try:
        # Step 1: Input Phase
        print("="*70)
        print("SJF SCHEDULER WITH THREADING SIMULATION")
        print("="*70)
        
        input_handler = ProcessInputHandler()
        processes = input_handler.input_processes()
        
        # Step 2: Scheduling Phase
        scheduler = SJFScheduler(processes)
        scheduled_processes = scheduler.calculate_metrics()
        
        # Step 3: Display calculated results
        OutputFormatter.print_results(scheduled_processes)
        
        # Step 4: Threading simulation (optional visual demonstration)
        user_choice = input("Run threaded execution simulation? (y/n): ").strip().lower()
        if user_choice == 'y':
            scheduler.run_threaded_simulation(execution_speed=0.2)
            print("\nSimulation demonstrates concurrent thread execution.")
            print("In real OS, SJF is non-preemptive, but threads show concurrency concept.")
        
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user. Exiting gracefully...")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        raise  # Re-raise for debugging in development


if __name__ == "__main__":
    # Entry point - allows module to be imported without auto-execution
    main()

