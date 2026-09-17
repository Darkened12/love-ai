import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ChatShellComponent } from './chat-shell-component';

describe('AppShell', () => {
  let component: ChatShellComponent;
  let fixture: ComponentFixture<ChatShellComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ChatShellComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(ChatShellComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
