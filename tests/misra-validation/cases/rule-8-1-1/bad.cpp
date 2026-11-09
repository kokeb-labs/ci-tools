// Seeded violation: a lambda kept in a variable captures this through a default capture.
#include <cstdint>

namespace kv::rule_8_1_1::bad {

class Counter {
 public:
  std::uint32_t read() {
    auto f = [&]() { return count_; };  // seeded
    return f();
  }

 private:
  std::uint32_t count_{0U};
};

}  // namespace kv::rule_8_1_1::bad
