import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ChatDeleteModalComponent } from './chat-delete-modal-component';

describe('ChatDeleteModalComponent', () => {
  let component: ChatDeleteModalComponent;
  let fixture: ComponentFixture<ChatDeleteModalComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ChatDeleteModalComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(ChatDeleteModalComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
