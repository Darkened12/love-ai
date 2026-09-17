import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MemoryComponent } from './memory-component';

describe('Memory', () => {
  let component: MemoryComponent;
  let fixture: ComponentFixture<MemoryComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MemoryComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(MemoryComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
