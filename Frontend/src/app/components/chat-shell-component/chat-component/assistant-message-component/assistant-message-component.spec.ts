import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AssistantMessageComponent } from './assistant-message-component';

describe('AssistantMessage', () => {
  let component: AssistantMessageComponent;
  let fixture: ComponentFixture<AssistantMessageComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AssistantMessageComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(AssistantMessageComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
