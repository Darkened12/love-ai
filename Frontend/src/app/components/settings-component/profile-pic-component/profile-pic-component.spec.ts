import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ProfilePicComponent } from './profile-pic-component';

describe('ProfilePicComponent', () => {
  let component: ProfilePicComponent;
  let fixture: ComponentFixture<ProfilePicComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ProfilePicComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(ProfilePicComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
