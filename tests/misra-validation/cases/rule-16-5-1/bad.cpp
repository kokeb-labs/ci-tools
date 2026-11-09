// Seeded violation: overloaded && and || lose short-circuit evaluation.
namespace kv::rule_16_5_1::bad {

struct Flag {
  bool set = false;
};

bool operator&&(Flag a, Flag b) { return a.set && b.set; }  // seeded
bool operator||(Flag a, Flag b) { return a.set || b.set; }  // seeded

}  // namespace kv::rule_16_5_1::bad
