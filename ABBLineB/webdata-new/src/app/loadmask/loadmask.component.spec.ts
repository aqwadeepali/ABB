import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { LoadmaskComponent } from './loadmask.component';

describe('LoadmaskComponent', () => {
  let component: LoadmaskComponent;
  let fixture: ComponentFixture<LoadmaskComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ LoadmaskComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(LoadmaskComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
