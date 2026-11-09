// Edge case: a floating literal with a lower-case l suffix (long double).
namespace kv::rule_5_13_5::bad_float {

long double ratio() { return 3.4l; }  // seeded

}  // namespace kv::rule_5_13_5::bad_float
