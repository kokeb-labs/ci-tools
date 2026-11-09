// Seeded violations of KB-CPP-046: a nested Result class, and an explicit specialisation that drops [[nodiscard]].
#include <cstdint>

namespace kv::kb_cpp_046::bad_nested {

enum class Error : std::uint8_t { kNone, kBus };

class Driver {
 public:
  class Result {
   public:
    Error error{Error::kNone};
  };
};

template <typename T>
struct [[nodiscard]] Result {
  T value{};
  Error error{Error::kNone};
};

template <>
struct Result<void> {
  Error error{Error::kNone};
};

}  // namespace kv::kb_cpp_046::bad_nested
