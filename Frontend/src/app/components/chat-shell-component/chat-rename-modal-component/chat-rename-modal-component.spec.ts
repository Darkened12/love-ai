import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ChatRenameModalComponent } from './chat-rename-modal-component';

describe('ChatRenameModalComponent', () => {
  let component: ChatRenameModalComponent;
  let fixture: ComponentFixture<ChatRenameModalComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ChatRenameModalComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(ChatRenameModalComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
