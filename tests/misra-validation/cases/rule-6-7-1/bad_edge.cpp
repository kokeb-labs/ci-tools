// Edge cases: more forms of the violation.
#include <cstdint>

namespace kv::rule_6_7_1::bad_edge {

class Sampler {
 public:
  std::int32_t next() {
    static std::int32_t calls = 0;  // a mutable static local in a member function
    ++calls;
    return calls;
  }
};
std::int32_t via_lambda() {
  const auto f = []() {
    static std::int32_t hits = 0;  // a mutable static local in a lambda
    ++hits;
    return hits;
  };
  return f();
}

}  // namespace kv::rule_6_7_1::bad_edge
