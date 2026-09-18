import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RelationshipModalComponent } from './relationship-modal-component';

describe('RelationshipComponent', () => {
  let component: RelationshipModalComponent;
  let fixture: ComponentFixture<RelationshipModalComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RelationshipModalComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(RelationshipModalComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
