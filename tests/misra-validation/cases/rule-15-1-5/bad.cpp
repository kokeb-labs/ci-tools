// Seeded violation: a class offers an initializer_list constructor and another non-special constructor.
#include <cstddef>
#include <cstdint>
#include <initializer_list>

namespace kv::rule_15_1_5::bad {

class Samples {
 public:
  Samples(std::initializer_list<std::uint16_t> values) : count_(values.size()) {}
  Samples(std::size_t count, std::uint16_t fill) : count_(count + (fill * 0U)) {}

 private:
  std::size_t count_;
};

}  // namespace kv::rule_15_1_5::bad
