// Seeded violation: a copy assignment that takes a non-const reference and returns by value.
#include <cstdint>

namespace kv::rule_15_0_2::bad {

class Counter {
 public:
  Counter() = default;
  Counter(const Counter&) = default;
  Counter(Counter&&) noexcept = default;
  Counter operator=(Counter& other) {  // seeded
    count_ = other.count_;
    return *this;
  }
  Counter& operator=(Counter&&) & noexcept = default;
  ~Counter() = default;

 private:
  std::uint32_t count_ = 0U;
};

}  // namespace kv::rule_15_0_2::bad
