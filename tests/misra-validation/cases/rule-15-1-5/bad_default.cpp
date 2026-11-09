// Seeded violation (default): an initializer_list constructor next to a default constructor.
#include <cstddef>
#include <cstdint>
#include <initializer_list>

namespace kv::rule_15_1_5::bad_default {

class Samples {
 public:
  Samples() : count_(0U) {}  // seeded
  Samples(std::initializer_list<std::uint16_t> values) : count_(values.size()) {}

  [[nodiscard]] std::size_t count() const { return count_; }

 private:
  std::size_t count_;
};

}  // namespace kv::rule_15_1_5::bad_default
