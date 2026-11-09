// Edge cases: more forms of the violation.

namespace kv::dir_0_3_1_nan::bad_edge {

// A possibly-NaN quotient tested for equality.
bool is_half(double a, double b) { return (a / b) == 0.5; }

// A possibly-NaN quotient compared inside a lambda.
bool any_above(double a, double b, double limit) {
  const auto above = [limit](double x, double y) { return (x / y) >= limit; };
  return above(a, b);
}

}  // namespace kv::dir_0_3_1_nan::bad_edge
