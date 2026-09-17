import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SystemPromptComponent } from './system-prompt-component';

describe('SystemPrompt', () => {
  let component: SystemPromptComponent;
  let fixture: ComponentFixture<SystemPromptComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SystemPromptComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(SystemPromptComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
