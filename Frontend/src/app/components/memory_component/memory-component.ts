import { Component } from '@angular/core';
import { NavbarComponent } from '../navbar-component/navbar-component';
import { MemoryService } from '../../services/memory-service';
import { BehaviorSubject } from 'rxjs';
import { Memory } from '../../models/memory-models';
import { AsyncPipe, DatePipe } from '@angular/common';

@Component({
  selector: 'app-memory-component',
  standalone: true,
  imports: [NavbarComponent, AsyncPipe, DatePipe],
  templateUrl: './memory-component.html',
  styleUrl: './memory-component.scss',
})
export class MemoryComponent {
  private memoryListSubject = new BehaviorSubject<Memory[]>([]);
  memoryList$ = this.memoryListSubject.asObservable();
  private loadingSubject = new BehaviorSubject<boolean>(true);
  loading$ = this.loadingSubject.asObservable();

  selectedMemory!: Memory
  showDeleteModal = false;

  constructor(private memoryService: MemoryService) {}

  showModal(memory: Memory) {
    this.showDeleteModal = true;
    this.selectedMemory = memory;
  }

  closeModal () {
    this.showDeleteModal = false;
  }

  deleteMemory() {
    if (this.selectedMemory) {
      this.memoryService.deleteMemory(this.selectedMemory).subscribe({
        next: () => {
          const memories = this.memoryListSubject.value;

          this.memoryListSubject.next(
            memories.filter(m => m.id !== this.selectedMemory.id)
          );
          this.closeModal();
        }
      });
    }
  }

  ngOnInit() {
    this.memoryService.getMemoryList().subscribe(
      memoryList => {
        this.memoryListSubject.next(memoryList);
        this.loadingSubject.next(false);
      }
    )
  }
}
