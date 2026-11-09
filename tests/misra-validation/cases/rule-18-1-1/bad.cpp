// Seeded violation: throwing a pointer.
namespace kv::rule_18_1_1::bad {

struct Fault {};

void fail() {
  static Fault fault;
  throw &fault;  // seeded
}

}  // namespace kv::rule_18_1_1::bad
